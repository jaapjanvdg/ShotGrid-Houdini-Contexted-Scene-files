import hou
from HDABuilder import HDABuilder

class DopSwitchNode(HDABuilder.HDABuilder):
    """

Build in the Houdini Python Console:


from importlib import reload

from NFA_Switch import dopSwitch_node
from HDABuilder import HDABuilder

reload(dopSwitch_node)
reload(HDABuilder)

dopSwitch_node.DopSwitchNode(
    name="nfa_dopswitch",
    hda_file_name="C:/pipeline/houdini/hsite/houdini21.0/otls/nfa_dopswitch.hdanc",
    description="nfa_dopswitch",
    min_num_inputs=0,
    max_num_inputs=99,
    max_num_outputs=1,
    version="1.0",
    hda_type=HDABuilder.HDATypes.DOPNET,
    icon="C:/pipeline/houdini/hsite/houdini21.0/otls/logo.svg",
    node_shape=HDABuilder.NodeShapes.DIAMOND
    )

    """
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            builded_nodes=self.build_hda_nodes,
            parameter_interface=self.build_hda_parms,
            **kwargs
            )
        self.build()

    def build_hda_parms(self):
        hou_parm_template_group = hou.ParmTemplateGroup()

        clean = hou.ButtonParmTemplate(
            "clean",
            "Switch Call",
            script_callback="from Utility import utility; utility.individual_switch(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )

        hou_parm_template_group.append(clean)

        return hou_parm_template_group



    def build_hda_nodes(self):

        hda_node = self.hda

        switch = hda_node.createNode("switch", "nfa_switch")

        for i in range(99):
            switch.setInput(i, hda_node.item(str(i + 1)))

        output = hda_node.createNode("subnetoutput")
        output.setInput(0, switch)
        
        hda_node.layoutChildren()

