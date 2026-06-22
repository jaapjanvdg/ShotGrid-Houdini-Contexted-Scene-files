import hou
from pathlib import Path
from Utility import utility
import shutil

def no_personal_task_error():
    hou.ui.displayMessage(
        "Please Fill in a Task",
        buttons=("OK",),
        severity=hou.severityType.Error
    )

def start(node):
    cache_cleanup(node)
    if node.isLockedHDA():
        node.allowEditingOfContents()
    personal_task_name = node.parm("task").eval()
    if not personal_task_name:
        no_personal_task_error()
        return
    path = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache()
    if not path:
        return
    rop_out = node.node("ROP_GEO")
    rop_out.parm("sopoutput").set(str(path))
    node.parm("load_from_disk").set(1)
    file = node.node("FILE_IN")
    file.parm("file").set(str(path))

    rop_out.render()

def start_bg(node):
        hou.ui.displayMessage(
        "This button does not work yet.",
        buttons=("OK",),
        severity=hou.severityType.Message
    )

def start_farm(node):
    cache_cleanup(node)
    if node.isLockedHDA():
        node.allowEditingOfContents()
    personal_task_name = node.parm("task").eval()
    if not personal_task_name:
        no_personal_task_error()
        return
    path = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache()
    if not path:
        return
    rop_out = node.node("ROP_GEO")
    rop_out.parm("sopoutput").set(str(path))

    file = node.node("FILE_IN")
    file.parm("file").set(str(path))
    node.parm("load_from_disk").set(1)
    hou.hipFile.save()
    deadline = node.node("DEADLINE")
    
    if node.parm("is_sim").eval():
        frame = deadline.node("FRAME_DEPENDENT")
        frame.parm("dl_Submit").pressButton()

    else:
        non = deadline.node("NON_FRAME_DEPENDENT")
        non.parm("dl_Submit").pressButton()

def cache_cleanup(node):
    """deletes old caches"""
    state = node.parm("auto_deletion").eval()
    if not state:
        return
    
    personal_task_name = node.parm("task").eval()
    if not personal_task_name:
        no_personal_task_error()
        return
    versions = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache_versions()
    if not versions:
        return

    keep_amount = int(node.parm("last_amount").eval())
    sorted_versions = sorted(versions, key=lambda p: str(p.name))

    kept_versions = sorted_versions[-keep_amount:]
    ready_for_deletions = sorted_versions[:-keep_amount]

    readable_kept_versions = []
    readable_ready_for_deletion = []
    for kept_version in kept_versions:
        readable_kept_versions.append(kept_version.name)

    for ready_for_deletion in ready_for_deletions:
        readable_ready_for_deletion.append(ready_for_deletion.name)
    if not ready_for_deletions:
        return
    choice = hou.ui.displayConfirmation(
        f"You are about to delete {readable_ready_for_deletion}.\n {readable_kept_versions} will be kept.\nDo you want to proceed?",
        severity=hou.severityType.Warning,
        title="Confirm Deletion"
    )

    if not choice:
        return
    
    for folder in ready_for_deletions:

        if not folder.exists():
            continue

        if not folder.is_dir():
            continue

        shutil.rmtree(folder)

def cache_selection_menu(node):
    personal_task_name = node.parm("task").eval()
    if not personal_task_name:
        no_personal_task_error()
        return
    versions = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache_versions()
    if not versions:
        return ["none", "No versions found"]

    menu = []
    for version in versions:
        label = version.name
        menu.extend([label, label])

    return menu

def collect_cache_selection(node) -> list[Path]:
    personal_task_name = node.parm("task").eval()
    if not personal_task_name:
        no_personal_task_error()
        return
    versions = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache_versions()
    if not versions:
        return ["none", "No versions found"]
    
    selections = node.parm("cache_selection").eval().split()

    selection_list = []

    for version in versions:
        for selection in selections:
            if version.name == selection:
                selection_list.append(version)
        
    return selection_list

def calculate_selection(node):
    selections = collect_cache_selection(node)

    gb_total = utility.calculate_folders_in_gb(selections)

    node.parm("size").set(gb_total)


def trash(node):

    selections = collect_cache_selection(node)
    versions = []
    for selection in selections:
        versions.append(selection.name)

    choice = hou.ui.displayConfirmation(
        f"You are about to delete {versions}.\nDo you want to proceed?",
        severity=hou.severityType.Warning,
        title="Confirm Deletion"
    )

    if not choice:
        return
    
    for folder in selections:

        if not folder.exists():
            continue

        if not folder.is_dir():
            continue

        shutil.rmtree(folder)


