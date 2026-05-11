from Utility import utility

def start(node):
    if node.isLockedHDA():
        node.allowEditingOfContents()
    rop = node.node("nfa_usd_rop")
    path = utility.ContextedPath(node=node).usd()
    if not path:
        return
    rop.parm("lopoutput").set(str(path))
    rop.render()