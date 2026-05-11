from pxr import Kind, Sdf, Usd
from pathlib import Path
import hou
from Utility import utility, constants

def parm_create(node, project: str, sequences: list[str]):
    project_parm = hou.MenuParmTemplate(
        "project",
        "Project",
        menu_items=([f"{project}"]),
        menu_labels=([f"{project}"]),
        item_generator_script="",
        item_generator_script_language=hou.scriptLanguage.Python,
        script_callback_language=hou.scriptLanguage.Python,
        menu_type=hou.menuType.Normal,
        menu_use_token=False, is_button_strip=False,
        strip_uses_icons=False,
        join_with_next=True
    )

    sequence_parm = hou.MenuParmTemplate(
        "seq",
        "Sequence",
        menu_items=(sequences),
        menu_labels=(sequences),
        item_generator_script="",
        item_generator_script_language=hou.scriptLanguage.Python,
        script_callback_language=hou.scriptLanguage.Python,
        script_callback=("from NFA_Context_Manager import contextManager; contextManager.update_shot(hou.pwd())"),
        menu_type=hou.menuType.Normal,
        menu_use_token=False,
        is_button_strip=False,
        strip_uses_icons=False,
        join_with_next=True
    )

    shot_parm = hou.MenuParmTemplate(
        "shot",
        "Shot",
        menu_items=(["Select_a_Sequence"]),
        menu_labels=(["Select a Sequence"]),
        item_generator_script="",
        item_generator_script_language=hou.scriptLanguage.Python,
        script_callback_language=hou.scriptLanguage.Python,
        menu_type=hou.menuType.Normal,
        menu_use_token=False,
        is_button_strip=False,
        strip_uses_icons=False
    )

    project_label = hou.LabelParmTemplate(
        "label_project",
        "Project: ",
        join_with_next=True,
        column_labels=([f"{project}"])
    )

    sequence_label = hou.LabelParmTemplate(
        "label_sequence",
        "Sequence: ",
        join_with_next=True,
        column_labels=([""])
    )

    shot_label = hou.LabelParmTemplate(
        "label_shot",
        "Shot: ",
        column_labels=([""])
    )

    get_context_button = hou.ButtonParmTemplate(
        "get_context",
        "Get Context",
        script_callback_language=hou.scriptLanguage.Python,
        script_callback=("from NFA_Context_Manager import contextManager; contextManager.get_context(hou.pwd())")
    )

    template_group = node.parmTemplateGroup()
    if not template_group.find("project"):
        template_group.append(project_parm)
        template_group.append(sequence_parm)
        template_group.append(shot_parm)
        template_group.append(project_label)
        template_group.append(sequence_label)
        template_group.append(shot_label)
        template_group.append(get_context_button)
        node.setParmTemplateGroup(template_group)
    else:
        project = template_group.find("project")
        template_group.replace(project, project_parm)
        seq = template_group.find("seq")
        template_group.replace(seq, sequence_parm)
        shot = template_group.find("shot")
        template_group.replace(shot, shot_parm)
        old_project_label = template_group.find("label_project")
        template_group.replace(old_project_label, project_label)
        old_seq_label = template_group.find("label_sequence")
        template_group.replace(old_seq_label, sequence_label)
        old_shot_label = template_group.find("label_shot")
        template_group.replace(old_shot_label, shot_label)
        old_get_button = template_group.find("get_context")
        template_group.replace(old_get_button, get_context_button)
        node.setParmTemplateGroup(template_group)

def set_shot_parm(node, sequence_shot_list: list[list[str]]):
    real_state = node.parm("seq").evalAsString()
    for seq, shots in sequence_shot_list:
        utility.set_sequence_context_label(node, real_state)
        if real_state == seq:
            shot_parm = hou.MenuParmTemplate(
                "shot",
                "Shot",
                menu_items=(shots),
                menu_labels=(shots),
                item_generator_script="",
                item_generator_script_language=hou.scriptLanguage.Python,
                script_callback=("from NFA_Context_Manager import contextManager; contextManager.update_context(hou.pwd())"),
                script_callback_language=hou.scriptLanguage.Python,
                menu_type=hou.menuType.Normal,
                menu_use_token=False,
                is_button_strip=False,
                strip_uses_icons=False
            )

            template_group = node.parmTemplateGroup()
            if not template_group.find("shot"):
                template_group.append(shot_parm)
                node.setParmTemplateGroup(template_group)
            else:
                shot = template_group.find("shot")
                template_group.replace(shot, shot_parm)
                node.setParmTemplateGroup(template_group)
            utility.set_shot_context_label(node, shots[0])
            node.parm("seq").set(real_state)

class CollectProject:
    def __init__(
            self,
            node: hou.node,
            ):
        
        self.node = node

        self.collect_project()

    def collect_project(self):
        project_name = utility.get_project_name()
        
        sg_project = utility.get_sg_project(project_name)
        sg_sequences = utility.get_sg_sequences(sg_project)
        utility.set_project_context_option(project_name)
        sequences_list = utility.get_sequence_list(sg_sequences)

        parm_create(self.node, str(project_name), sequences_list)

def update_shot(node):
    sg_project = utility.get_sg_project(utility.get_project_name())
    sg_sequences = utility.get_sg_sequences(sg_project)
    sequence_shot_list = utility.get_sequence_shot_list(sg_sequences)
    set_shot_parm(node, sequence_shot_list)

def update_context(node):
    real_state = node.parm("shot").evalAsString()
    utility.set_shot_context_label(node, real_state)

def get_context(node):
    project = node.parm("label_project").eval()
    sequence = node.parm("label_sequence").eval()
    shot = node.parm("label_shot").eval()
    utility.set_sequence_context_option(sequence)
    utility.set_shot_context_option(shot)

    if shot == "":
        hou.ui.displayMessage("Please select a sequence", buttons=("OK",), severity=hou.severityType.Error)
        return

    hou.setUpdateMode(hou.updateMode.Manual)

    durations = utility.get_cut_duration(sequence, shot)
    cut_in = durations[0]
    cut_out = durations[1]
    hou.playbar.setFrameRange(cut_in, cut_out)
    hou.playbar.setPlaybackRange(cut_in, cut_out)
    hou.setFrame(cut_in)

    main_usd_path = get_main_usd_filepath(project, sequence, shot)
    if not main_usd_path:
        return
    sublayers = get_sublayers(sequence, shot)
    create_sub_usdas(sequence, shot)
    get_main_usd(main_usd_path, sublayers)

    create_usd_import(main_usd_path)

    set_fetch_button()
    utility.switch_all_inputs()

    shot_id = utility.get_sg_shot_id(project, sequence, shot)
    fx_id = utility.get_fx_task(shot_id)
    utility.set_fx_id_context_option(fx_id)

    hou.setUpdateMode(hou.updateMode.AutoUpdate)


def create_usd_import(path_to_main_usd):
    lopnet = hou.node('/obj/LOPNET')
    if not lopnet:
        obj = hou.node('/obj')
        lopnet = obj.createNode("lopnet", "LOPNET")
    found = False
    for node in lopnet.children():
        if node.type().name() == "NFA_layerstack_loader":
            found = True
            break

    if not found:
        node = lopnet.createNode("NFA_layerstack_loader")

    if node.isLockedHDA():
        node.allowEditingOfContents()
    in_node = node.node("Layerstack")
    in_node.parm(f"num_files").set("1")
    in_node.parm(f"filepath1").set(str(path_to_main_usd))

def get_main_usd_filepath(project, sequence, shot):
    current_filepath = utility.ContextedPath().file_path

    project_path = current_filepath.parents[-3]
    publish = "04_publish"
    step = "shots"
    usda_path = Path(project_path) / publish / step / sequence / shot
    if not usda_path.exists():
        usda_path.mkdir(parents=True, exist_ok=False)
    full_file_name = f"{project}_{sequence}_{shot}_main_layerstack.usda"
    usd_path = Path(usda_path) / full_file_name
    return usd_path.as_posix()
    
def get_main_usd(path_to_main_usd, sublayers):

    root_layer = Sdf.Layer.FindOrOpen(str(path_to_main_usd))
    if not root_layer:
        root_layer = Sdf.Layer.CreateNew(str(path_to_main_usd))
    for sublayer in sublayers:
        if sublayer not in root_layer.subLayerPaths:
            root_layer.subLayerPaths.append(str(sublayer))
    root_layer.Save()

def get_sublayers(sequence, shot):
    current_filepath = utility.ContextedPath().file_path
    file_name = current_filepath.stem
    split_filename = file_name.split("_")
    project_number = split_filename[0]

    sublayers = []

    steps = constants.ContextPaths.STEPLIST

    for step in steps:
        usd_filename = f"{project_number}_sc{sequence}_{shot}_{step}_work_main.usda"
        full_usd_path = Path(step) / usd_filename
        sublayers.append(full_usd_path.as_posix())
    return sublayers

def create_sub_usdas(sequence, shot):
    current_filepath = utility.ContextedPath().file_path

    project_path = current_filepath.parents[-3]
    publish = "04_publish"
    shots_step = "shots"
    file_name = current_filepath.stem
    split_filename = file_name.split("_")
    project_number = split_filename[0]

    steps = constants.ContextPaths.STEPLIST

    for step in steps:
        usda_path = Path(project_path) / publish / shots_step / sequence / shot / step
        if not usda_path.exists():
            usda_path.mkdir(parents=True, exist_ok=False)

        root_layer = Sdf.Layer.FindOrOpen(f"{usda_path}/{project_number}_sc{sequence}_{shot}_{step}_work_main.usda")
        if not root_layer:
            root_layer = Sdf.Layer.CreateNew(f"{usda_path}/{project_number}_sc{sequence}_{shot}_{step}_work_main.usda")
        
        root_layer.Save()

def check_cache_node(node)->bool:
    source_path = node.parm("source").eval()
    if not source_path:
        return
    source_path_steps = source_path.split("/")
    node_path = "/".join(source_path_steps[:-1])
    
    source_node = hou.node(node_path)
    if not source_node:
        hou.ui.displayMessage(f"WARNING {source_path} is not findable in fetchnode:{node}", buttons=("OK",), severity=hou.severityType.Error)
        return
    if source_node.type().name() == "nfa_filecache":
        return True
    else:
        return False

def set_fetch_button():
    fetch_nodes = utility.get_nodes_by_name_workspace("fetch", "ropnet")
    for node in fetch_nodes:
        if check_cache_node(node):
            render_parm = hou.ButtonParmTemplate(
                "render_parm",
                "NFA render",
                script_callback_language=hou.scriptLanguage.Python,
                join_with_next=True,
                script_callback=("from NFA_Context_Manager import contextManager; contextManager.render_fetch(hou.pwd())")
            )
            set_path_parm = hou.ButtonParmTemplate(
                "set_path",
                "set path",
                script_callback_language=hou.scriptLanguage.Python,
                script_callback=("from NFA_Context_Manager import contextManager; contextManager.set_fetch_path(hou.pwd())")
            )
            template_group = node.parmTemplateGroup()
            if not template_group.find("set_path"):
                template_group.append(set_path_parm)
                node.setParmTemplateGroup(template_group)
            elif template_group.find("set_path") and not template_group.find("render_parm"):
                old_get_button = template_group.find("set_path")
                template_group.replace(old_get_button, set_path_parm)
                template_group.append(render_parm)
                node.setParmTemplateGroup(template_group)
            else:
                old_render_button = template_group.find("render_parm")
                template_group.replace(old_render_button, render_parm)
                old_get_button = template_group.find("set_path")
                template_group.replace(old_get_button, set_path_parm)
                node.setParmTemplateGroup(template_group)

def render_fetch(node):
    source_path = node.parm("source").eval()
    source_path_node = hou.node(source_path)
    source_path_steps = source_path.split("/")
    node_path = "/".join(source_path_steps[:-1])

    source_node = hou.node(node_path)
    if source_node.type().name() == "nfa_filecache":
        source_node.parm("save_to_disk").pressButton()
        return
    elif source_node.type().name() == "NFA_usd_out":
        source_node.parm("set_path").pressButton()
        return
    elif source_path_node.type().name() == "karmarenderproperties":
        karma_path = utility.ContextedPath().karma()
        source_path_node.parm("picture").set(str(karma_path))
        return

def set_fetch_path(node):
    source_path = node.parm("source").eval()
    source_path_node = hou.node(source_path)
    source_path_steps = source_path.split("/")
    node_path = "/".join(source_path_steps[:-1])

    source_node = hou.node(node_path)
    if source_node.type().name() == "nfa_filecache":
        set_cache_path(source_node)
        return
    elif source_node.type().name() == "NFA_usd_out":
        # add things in future
        return
    elif source_path_node.type().name() == "karmarenderproperties":
        # add things in future
        return

def set_cache_path(node):
    if node.isLockedHDA():
        node.allowEditingOfContents()
    personal_task_name = node.parm("task").eval()
    path = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache()
    if not path:
        return
    rop_out = node.node("ROP_GEO")
    rop_out.parm("sopoutput").set(str(path))

    file = node.node("FILE_IN")
    file.parm("file").set(str(path))
    node.parm("load_from_disk").set(1)
    hou.hipFile.save()