import hou
from pathlib import Path
from Utility import utility
import shutil

def start(node):
    copyprim(node)
    usd_cleanup(node)
    if node.isLockedHDA():
        node.allowEditingOfContents()
    rop = node.node("nfa_usd_rop")
    path = utility.ContextedPath(node=node).usd()
    if not path:
        return
    rop.parm("lopoutput").set(str(path))
    rop.render()

def copyprim(node):
    usd_rop = node.node("nfa_usd_rop")
    prim_value = node.parm("defaultprim").evalAsString()
    usd_rop.parm("defaultprim").set(prim_value)

def usd_cleanup(node):
    """deletes old usds"""
    state = node.parm("auto_deletion").eval()
    if not state:
        return

    versions = utility.ContextedPath(node=node).usd_versions()
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

def usd_selection_menu(node):
    versions = utility.ContextedPath(node=node).usd_versions()
    if not versions:
        return ["none", "No versions found"]

    menu = []
    for version in versions:
        label = version.name
        menu.extend([label, label])

    return menu

def collect_usd_selection(node) -> list[Path]:
    versions = utility.ContextedPath(node=node).usd_versions()
    if not versions:
        return ["none", "No versions found"]
    
    selections = node.parm("usd_selection").eval().split()

    selection_list = []

    for version in versions:
        for selection in selections:
            if version.name == selection:
                selection_list.append(version)
        
    return selection_list

def calculate_selection(node):
    selections = collect_usd_selection(node)

    gb_total = utility.calculate_folders_in_gb(selections)

    node.parm("size").set(gb_total)


def trash(node):

    selections = collect_usd_selection(node)
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


