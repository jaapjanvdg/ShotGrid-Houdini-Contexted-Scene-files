import hou
from HDABuilder import HDABuilder

class UsdOutNode(HDABuilder.HDABuilder):
    """

Build in the Houdini Python Console:


from importlib import reload

from NFA_USD_Out import usdOut_node
from HDABuilder import HDABuilder

reload(usdOut_node)
reload(HDABuilder)

usdOut_node.UsdOutNode(
    name="NFA_usd_out",
    hda_file_name="C:/pipeline/houdini/hsite/houdini21.0/otls/NFA_usd_out.hdanc",
    description="NFA_usd_out",
    min_num_inputs=1,
    max_num_inputs=1,
    max_num_outputs=0,
    version="1.0",
    hda_type=HDABuilder.HDATypes.LOPNET,
    icon="C:/pipeline/houdini/hsite/houdini21.0/otls/logo.svg",
    node_shape=HDABuilder.NodeShapes.CLIPPED_LEFT
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

        set_path = hou.ButtonParmTemplate(
            "set_path",
            "Save to Disk",
            script_callback="from NFA_USD_Out import usdOut; usdOut.start(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )
        
        folder_prims_control = hou.FolderParmTemplate(
            "folder_prims_control",
            "Primitives Control",
            folder_type=hou.folderType.Tabs,
            default_value=0,
            ends_tab_group=False
            )
        
        folder_version_cleanup = hou.FolderParmTemplate(
            "folder_version_cleanup",
            "Version Cleanup",
            folder_type=hou.folderType.Tabs,
            default_value=0,
            ends_tab_group=False
            )

        trash = hou.ButtonParmTemplate(
            "trash",
            "Trash selected",
            is_label_hidden=True,
            join_with_next=True,
            script_callback="from NFA_USD_Out import usdOut; usdOut.trash(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )
        trash.setTags({"button_icon": "C:/pipeline/houdini/hsite/houdini21.0/otls/trash_icon.png"})

        usd_selection = hou.StringParmTemplate(
            "usd_selection",
            "Usd Selection",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="from NFA_USD_Out import usdOut \nreturn usdOut.usd_selection_menu(hou.pwd())",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.StringToggle,
            join_with_next=True,
            script_callback_language=hou.scriptLanguage.Python
            )

        calculate = hou.ButtonParmTemplate(
            "calculate",
            "Calculate Selected",
            join_with_next=True,
            script_callback="from NFA_USD_Out import usdOut; usdOut.calculate_selection(hou.pwd())",
            script_callback_language=hou.scriptLanguage.Python
            )
        
        size = hou.StringParmTemplate(
            "size",
            "Total Size",
            1,
            default_value=([""]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=([]),
            menu_labels=([]),
            icon_names=([]),
            item_generator_script="",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.Normal,
            script_callback_language=hou.scriptLanguage.Python
            )

        auto_deletion = hou.ToggleParmTemplate(
            "auto_deletion",
            "Auto Deletion",
            default_value=True,
            script_callback_language=hou.scriptLanguage.Python,
            join_with_next=True
            )

        last_amount = hou.StringParmTemplate(
            "last_amount",
            "Preserve Recent Number Of Versions",
            1,
            default_value=(["1"]),
            naming_scheme=hou.parmNamingScheme.Base1,
            string_type=hou.stringParmType.Regular,
            menu_items=(["1","2","3","4","5","6"]),
            menu_labels=(["1","2","3","4","5","6"]),
            icon_names=([]),
            item_generator_script="",
            item_generator_script_language=hou.scriptLanguage.Python,
            menu_type=hou.menuType.Normal,
            script_callback_language=hou.scriptLanguage.Python
            )
        last_amount.setConditional(hou.parmCondType.DisableWhen, "{ auto_deletion == 0 }")
        
        folder_version_cleanup_entries = (
            trash,
            usd_selection,
            calculate,
            size,
            auto_deletion,
            last_amount
        )
        for i in folder_version_cleanup_entries:
            folder_version_cleanup.addParmTemplate(i)

        node_entries = (
            set_path,
            folder_prims_control,
            folder_version_cleanup
            )
        

        for i in node_entries:
            hou_parm_template_group.append(i)

        return hou_parm_template_group

    def build_hda_nodes(self):
        expression1 = """ch("../defaultprim")"""

        hda_node = self.hda

        hda_input_node = hda_node.item("1")

        loppath = """../`opinput(".", 0)`"""
        usd_rop = hda_node.createNode("usd_rop", "nfa_usd_rop")
        usd_rop.setInput(0, hda_input_node)
        usd_rop.parm("trange").set(1)
        usd_rop.parm("loppath").set(loppath)
        usd_rop.parm("lopoutput").set("")
        usd_rop.parm("savestyle").set("flattenalllayers")
        usd_rop.parm("fileperframe").set(1)
        usd_rop.parm("trackprimexistence").set(1)
        usd_rop.parm("f1").setExpression("$FSTART")
        usd_rop.parm("f2").setExpression("$FEND")
        usd_rop.parm("defaultprim").setExpression(expression1)

        hda_node.layoutChildren()

