import hou
from Utility import utility

def start(node):
    if node.isLockedHDA():
        node.allowEditingOfContents()
    personal_task_name = node.parm("task").eval()
    path = utility.ContextedPath(personal_task_name=personal_task_name, node=node).cache()
    if not path:
        return
    rop_out = node.node("ROP_GEO")
    rop_out.parm("sopoutput").set(str(path))
    node.parm("load_from_disk").set(1)
    file = node.node("FILE_IN")
    file.parm("file").set(str(path))

    rop_out.render()

def start_farm(node):
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
    deadline = node.node("DEADLINE")
    
    if node.parm("is_sim").eval():
        frame = deadline.node("FRAME_DEPENDENT")
        frame.parm("dl_Submit").pressButton()

    else:
        non = deadline.node("NON_FRAME_DEPENDENT")
        non.parm("dl_Submit").pressButton()
