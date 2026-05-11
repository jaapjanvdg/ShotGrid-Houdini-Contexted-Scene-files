from pathlib import Path
import shotgun_api3 as shotgun
import hou
from typing import Any
from Utility import constants
from pxr import Sdf, Usd

SERVER_PATH = "FILL IN YOUR SERVER PATH"
SCRIPT_NAME = "FILL IN YOUR SCRIPT NAME"
SCRIPT_KEY = "FILL IN YOUR SCRIPT KEY"
shotgrid_connection = shotgun.Shotgun(SERVER_PATH, script_name=SCRIPT_NAME, api_key=SCRIPT_KEY)

def is_folder_empty(path: Path) -> bool:
    """Checks if folder is empty
    Args:
        path (Path): path to check.

    Returns:
        bool: true if folder is empty
    """
    for item in path.iterdir():
        if item.is_file():
            return True
        else:
            return False

def get_next_version(version_path: Path) -> str:
    """Returns the version you need
    Args:
        version_path (Path): version destination.

    Returns:
        string with version.
    Example:
        v001, v002
    """
    version_nums = []

    for file in version_path.iterdir():
        if file.is_dir() and file.name.startswith("v"):
            version_num = int(file.name[1:])
            version_nums.append(version_num)

    if not version_nums:
        return f"v001"
    
    latest_version = max(version_nums)
    configured_version = f"v{latest_version:03d}"
    latest_path = Path(version_path) / configured_version
    if not is_folder_empty(latest_path):
        return configured_version
    else:
        latest_version += 1
        return f"v{latest_version:03d}"

def get_latest_version(version_path: Path) -> str | None:
    """Returns the latest version you need
    Args:
        version_path (Path): version destination.

    Returns:
        version string.
    Example:
        v001, v002.
    """
    version_nums = []
    for file in version_path.iterdir():
        if file.is_dir() and file.name.startswith("v"):
            version_num = int(file.name[1:])
            version_nums.append(version_num)

    if not version_nums:
        return
    
    latest_version = max(version_nums)
    return f"v{latest_version:03d}"

def get_nodes_by_name(node_name: str)->list:
    """Collects all nodes of a certain type in file.

    Args:
        node_name (str): name of the node by node type.

    Returns:
        list: all nodes found and in this list
    """
    nodes = []
    for node in hou.node("/").allSubChildren():
        if node.type().name() == node_name:
            nodes.append(node)
    return nodes

def get_nodes_by_name_workspace(node_name: str, workspace: str)->list:
    """Collects all nodes of a certain type on OBJ level.

    Args:
        node_name (str): name of the node by node type.
        workspace (str): name of the workspace type

    Returns:
        list: all nodes found and in this list
    """
    nodes = []
    obj = hou.node(f"/obj")
    for net in obj.children():
        if net.type().name() == workspace:
            for node in net.children():
                if node.type().name() == node_name:
                    nodes.append(node)
    return nodes

def get_sg_project(project_name: str) -> dict[str, Any]:
    project = shotgrid_connection.find_one(
    "Project",
    [["name", "is", project_name]],
    ["id", "name"])
    return project
    
def get_sg_sequences(project: dict[str, Any]) -> list[dict[str, Any]]:
    sequences = shotgrid_connection.find(
    "Sequence",
    [["project", "is", project]],
    ["id", "code", "description"])
    return sequences

def get_sg_shot_id(project, sequence, shot):
    """
    Uses shotgrid to get ID
    function is used for context manager related playblasts in houdini
    """
    project_id = shotgrid_connection.find_one(
        "Project",
        [["name", "is", project]],
        ["id"]
    )

    sequence_id = shotgrid_connection.find_one(
        "Sequence",
        [
            ["project", "is", project_id],
            ["code", "is", sequence]
        ],
        ["id"]
    )

    shot_id = shotgrid_connection.find_one(
        "Shot",
        [
            ["project", "is", project_id],
            ["sg_sequence", "is", sequence_id],
            ["code", "is", shot]
        ],
        ["id"]
    )
    return shot_id["id"]

def get_fx_task(shot_id):
    """
    Uses shotgrid to get ID
    make sure to check if this returns something in the case a fx task does not
    excist in Shotgrid
    function is used for context manager related playblasts in houdini
    Args:
        shot_id: (int) shotgrid shot id
    """
    task = shotgrid_connection.find_one(
        "Task",
        [
            ["entity", "is", {"type": "Shot", "id": shot_id}],
            ["step.Step.code", "is", "Effects"]
        ],
        ["id", "content", "step"]
    )
    if task:
        return task["id"]
    else:
        return "No fx task"

def get_sg_shots(sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shots = shotgrid_connection.find(
    "Shot",
    [["sg_sequence", "is", sequence]],
    ["id", "code", "description", "project"])
    return shots

def get_sequence_list(sg_sequences: list[dict[str, Any]]) -> list[str]:
    sequences = []
    for sequence in sorted(sg_sequences, key=lambda s: str(s["code"])):
        sequences.append(sequence["code"])
    return sequences

def get_sequence_shot_list(sg_sequences: list[dict[str, Any]]) -> list[list[str]]:
    sequences = []
    for sequence in sorted(sg_sequences, key=lambda s: str(s["code"])):
        sg_shots = get_sg_shots(sequence)
        shots = get_shot_list(sg_shots)
        sequences.append([sequence["code"], shots])
    return sequences

def get_shot_list(sg_shots: list[dict[str, Any]]) -> list[str]:
    shots = []
    for shot in sorted(sg_shots, key=lambda s: str(s["code"])):
        shots.append(shot["code"])
    return shots

def get_cut_duration(sequence, shot):
    sg_project = get_sg_project(str(get_project_name()))
    sg_sequences = get_sg_sequences(sg_project)

    for seq in sorted(sg_sequences, key=lambda s: str(s["code"])):
        if sequence == seq["code"]:
            list_shot = shotgrid_connection.find_one(
                "Shot",
                [
                    ["sg_sequence", "is", seq],
                    ["code", "is", shot]
                ],
                ["id", "code", "sg_cut_in", "sg_cut_out", "sg_cut_duration"]
            )

            cut_in = list_shot["sg_cut_in"]
            if cut_in is None:
                cut_in = 1001

            duration = list_shot["sg_cut_duration"]

            cut_out = list_shot["sg_cut_out"]
            if cut_out is None and duration is not None:
                cut_out = 1000 + duration
            
            if duration is None and cut_out is not None:
                duration = cut_out - 1000
            
            if duration is None:
                duration = 2
            
            if cut_out is None:
                cut_out = 1000 + duration

    return [cut_in, cut_out]

def set_project_context_option(project_name: str):
    hou.setContextOption("project_name", project_name)

def set_sequence_context_label(node, value):
    node.parm("label_sequence").set(str(value))

def set_shot_context_label(node, value):
    node.parm("label_shot").set(str(value))

def set_sequence_context_option(value):
    hou.setContextOption("sequence", value)

def set_shot_context_option(value):
    hou.setContextOption("shot", value)

def set_fx_id_context_option(value):
    hou.setContextOption("fx_id", value)

class ContextedPath:
    """Path maker for all context manager caches and usd's and other
    context dependent files.
    """
    def __new__(cls, *args, **kwargs):
        if not cls.filechecks():
            return
        return super().__new__(cls)

    def __init__(
            self,
            node: hou.node=None,
            personal_task_name: str=None,
            is_time_dependent: bool=True
            ):
        
        self.personal_task_name = personal_task_name
        self.node = node
        self.is_time_dependent = is_time_dependent

        self.file_path = Path(hou.hipFile.path())
        self.sequence = hou.contextOption("sequence")
        self.shot = hou.contextOption("shot")
        self.shot_step = constants.ContextPaths.SHOT_STEP
        parts = self.file_path.parts
        self.workfiles = parts[3]
        self.task_name = parts[5]
        self.file_name = self.file_path.stem
        self.project_path = self.file_path.parents[-3]
        self.project_name = self.project_path.stem
        self.split_filenames = self.file_name.split("_")
        self.project_number = self.split_filenames[0]

        self.task_step = self.split_filenames[1]
        if self.task_step == "cfx":
            self.task_step = constants.ContextPaths.STEPLIST[1]

    def cache_version_location(self) -> Path:
        if not self.personal_task_name:
            raise Exception
        cache_version_path = Path(self.project_path) / self.workfiles / self.shot_step / self.sequence / self.shot / self.task_step / self.task_name / self.personal_task_name
        cache_version_path.mkdir(parents=True, exist_ok=True)
        return cache_version_path

    def cache_file_name(self) -> str:
        if not self.personal_task_name:
            raise Exception
        return f"{self.project_number}_sc{self.sequence}_{self.shot}_{self.task_step}_{self.personal_task_name}_work_main"

    def gl_file_name(self) -> str:
        return f"{self.project_number}_sc{self.sequence}_{self.shot}_{self.task_step}_{self.task_name}"

    def cache(self) -> Path | None:
        """creates incremented cache path version
        Returns:
            Path: Full path or None 
        """
        if not self.node:
            return

        version_path = self.cache_version_location()
        cache_file_name = self.cache_file_name()
        extention = self.node.parm("filetype").evalAsString()
        version = get_next_version(version_path)

        if self.node.parm("time_dependent").eval() == 1:
            full_file_name = f"{cache_file_name}_{version}.$F4{extention}"
        else:
            full_file_name = f"{cache_file_name}_{version}{extention}"

        path = Path(version_path) / version
        path_return = Path(version_path) / version / full_file_name
        if not path.exists():
            path.mkdir(parents=True, exist_ok=False)

        deadline = self.node.node("DEADLINE") #separate function later for checking if cachenode uses correct hda
        frame = deadline.node("FRAME_DEPENDENT")
        frame.parm("dl_job_name").set(f"{cache_file_name}_SIM_{version}")
        non = deadline.node("NON_FRAME_DEPENDENT")
        non.parm("dl_job_name").set(f"{cache_file_name}_GEO_{version}")

        return path_return.as_posix()

    def switch_cache(self) -> Path | None:
        """Looks for the latest cache version excisting in the requested directory
        Returns:
            Path: Full path or None 
        """
        if not self.node:
            return

        version_path = self.cache_version_location()
        cache_file_name = self.cache_file_name()
        extention = self.node.parm("filetype").evalAsString()
        version = get_latest_version(version_path)
        if not version: return

        if self.is_time_dependent:
            full_file_name = f"{cache_file_name}_{version}.$F4{extention}"
        else:
            full_file_name = f"{cache_file_name}_{version}{extention}"

        path = Path(version_path) / version
        path_return = Path(version_path) / version / full_file_name
        path.mkdir(parents=True, exist_ok=True)

        return path_return.as_posix()

    def karma(self) -> Path | None:
        """creates incremented karma path version
        Returns:
            Path: Full path or None 
        """
        version_path = Path(self.project_path) / self.workfiles / self.shot_step / self.sequence / self.shot / self.task_step / self.task_name / constants.ContextPaths.FLIPBOOKS
        version_path.mkdir(parents=True, exist_ok=True)

        version = get_latest_version(version_path)
        if not version:
            return

        full_file_name = f"{self.gl_file_name()}_{version}.$F4{constants.ContextPaths.EXR}"
        path = Path(version_path) / version
        path.mkdir(parents=True, exist_ok=True)

        path_return = Path(version_path) / version / full_file_name
        return path_return.as_posix()
    
    def usd(self) -> Path | None:
        """creates incremented USD path version
        Returns:
            Path: Full path or None 
        """
        stage = self.node.stage()
        prims = list(stage.Traverse())
        prim_path = prims[0].GetPath().pathString
        given_task_name = prim_path.split("/")[-1]
        if given_task_name == "HoudiniLayerInfo":
            prim_path = prims[1].GetPath().pathString
            given_task_name = prim_path.split("/")[-1]

        if self.task_step == f"sc{self.sequence}":
            self.task_step = "anim"
        if self.task_step == "cfx":
            self.task_step = "fx"
        elif self.task_step not in constants.ContextPaths.STEPLIST:
            hou.ui.displayMessage(f"{self.task_step} is not a pipeline step", buttons=("OK",), severity=hou.severityType.Error)
            return
        
        version_path = Path(self.project_path) / constants.ContextPaths.PUBLISH / self.shot_step / self.sequence / self.shot /  self.task_step / constants.ContextPaths.USD / given_task_name
        version_path.mkdir(parents=True, exist_ok=True)

        usd_file_name = f"{self.project_number}_sc{self.sequence}_{self.shot}_{self.task_step}_work_main"
        version = get_next_version(version_path)

        full_file_name = f"{usd_file_name}_{version}.usd"
        path = Path(version_path) / version
        path_return = Path(version_path) / version / full_file_name
        path.mkdir(parents=True, exist_ok=True)

        usda_path = Path(self.project_path) / constants.ContextPaths.PUBLISH / self.shot_step / self.sequence / self.shot / self.task_step

        sublayer = Path(constants.ContextPaths.USD) / given_task_name / version / full_file_name
        
        root_layer = Sdf.Layer.FindOrOpen(f"{usda_path}/{self.project_number}_sc{self.sequence}_{self.shot}_{self.task_step}_work_main.usda")
        if not root_layer:
            root_layer = Sdf.Layer.CreateNew(f"{usda_path}/{self.project_number}_sc{self.sequence}_{self.shot}_{self.task_step}_work_main.usda")
        usd_file = Usd.Stage.Open(root_layer.identifier)
        Usd.StageCache().Clear()

        task_path = f"/sc{self.sequence}/sh{self.shot}/{self.task_step}/{self.given_task_name}"

        step_prim = usd_file.DefinePrim(task_path, "Xform")

        if not step_prim.GetReferences():
            step_prim.GetReferences().AddReference(str(sublayer.as_posix()))
        else:
            step_prim.GetReferences().ClearReferences()
            step_prim.GetReferences().AddReference(str(sublayer.as_posix()))
        Usd.ModelAPI(step_prim).SetKind("component")

        usd_file.GetRootLayer().Save()

        return path_return.as_posix()



    @classmethod
    def filechecks(cls)->bool:
        """Makes sure if the user's file has the correct requirements

        Returns:
            bool: only if everything passes it will return true, 
            else it will give the user a message and returns false

        """
        current_filepath = Path(hou.hipFile.path())
        if not current_filepath:
            hou.ui.displayMessage(
                "Houdini filepath not found, please open a file with shotgrid",
                buttons=("OK",),
                severity=hou.severityType.Error
                )
            return False

        parts = current_filepath.parts
        projects = parts[1]
        if not projects == "projects":
            hou.ui.displayMessage(
                "File not configured correctly!\n"
                "Open a Shotgrid file or contact your Pipeline TD'er",
                buttons=("OK",),
                severity=hou.severityType.Error
                )
            return False

        workfiles = parts[3]
        if not workfiles == "03_workfiles":
            hou.ui.displayMessage(
                "File not configured correctly!\n"
                "Open a Shotgrid file or contact your Pipeline TD'er",
                buttons=("OK",),
                severity=hou.severityType.Error
                )
            return False

        shot = hou.contextOption("shot")
        if not shot:
            hou.ui.displayMessage(
                "Please Select a Context",
                buttons=("OK",),
                severity=hou.severityType.Error
                )
            return False
        
        file_name = current_filepath.stem
        split_filename = file_name.split("_")
        project_number = split_filename[0]
        if not project_number:
            hou.ui.displayMessage(
                "This project needs a project code. Please fill in a Projectcode in the project details page of this project's Web App ",
                buttons=("OK",),
                severity=hou.severityType.Error
                )
            return False

        task_step = split_filename[1]
        if task_step == "cfx":
            task_step = constants.ContextPaths.STEPLIST[1]
        elif task_step not in constants.ContextPaths.STEPLIST:
            hou.ui.displayMessage(f"{task_step} is not a pipeline step", buttons=("OK",), severity=hou.severityType.Error)
            return
        
        return True
    
def get_project_name()->str:
    file_path = Path(hou.hipFile.path())
    if not file_path:
        hou.ui.displayMessage(
            "Houdini filepath not found, please open a file with shotgrid",
            buttons=("OK",),
            severity=hou.severityType.Error
            )
        return
    project_path = file_path.parents[-3]
    project_name = project_path.stem
    return str(project_name)


def delete_calls():
    """
    Loop to delete all calls
    """
    calls = hou.contextOptionChangeCallbacks()
    if not calls:
        return
    for call in calls:
        hou.removeContextOptionChangeCallback(call)

def switch_logic(nodes):
    """
    Toggles the switch input to the correct input.

    Args:
        nodes (list): all switch nodes.
    """
    if not nodes:
        return
    for node in nodes:
        if node.isLockedHDA():
            node.allowEditingOfContents()
        switch = node.node("nfa_switch")
        sequence = hou.contextOption("sequence")
        shot = hou.contextOption("shot")
        inputs = switch.inputs()
        full_name = f"{sequence}_{shot}"

        for i, input in enumerate(inputs):
            split_inputs = str(input).split("_")
            new_input = f"{split_inputs[0]}_{split_inputs[1]}"
            if new_input == full_name:
                switch.parm("input").set(i)
                break
            else:
                switch.parm("input").set(0)

def cache_logic(nodes):
    """
    Sets all the chache file paths depending on the context. 
    
    Args:
        nodes (list): all nfa cache nodes.
    
    """
    if not nodes:
        return
    for node in nodes:
        if node.isLockedHDA():
            node.allowEditingOfContents()
        personal_task_name = node.parm("task").eval()
        if not personal_task_name:
            continue
        path = ContextedPath(personal_task_name=personal_task_name, node=node).switch_cache()
        if not path:
            print(f"{node} could not find a path for {personal_task_name}")
            continue
        file = node.node("FILE_IN")
        file.parm("file").set(str(path))

def switch_all_inputs():
    cache_nodes = get_nodes_by_name("nfa_filecache")
    cache_logic(cache_nodes)
    switch_nodes = get_nodes_by_name("nfa_context_switch")
    switch_logic(switch_nodes)

def individual_switch(node):
    nodes = [node]
    switch_logic(nodes)
