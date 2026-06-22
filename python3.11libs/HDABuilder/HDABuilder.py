import logging
import hou
from typing import Callable


class HDATypes:
    CHANNEL = "chopnet"
    COMPOSITING = "copnet"
    COPERNICUS = "cop2net"
    DYNAMICS = "dopnet"
    LOPNET = "lopnet"
    OBJECT = "obj"
    RENDER = "ropnet"
    VEX = "vopnet"
    TOP = "topnet"
    SOPNET = "geo"

class NodeShapes:
    RECT = 'rect'
    BONE = 'bone'
    BULGE = 'bulge'
    BULGE_DOWN = 'bulge_down'
    BURST = 'burst'
    CAMERA = 'camera'
    CHEVRON_DOWN = 'chevron_down'
    CHEVRON_UP = 'chevron_up'
    CIGAR = 'cigar'
    CIRCLE = 'circle'
    CLIPPED_LEFT = 'clipped_left'
    CLIPPED_RIGHT = 'clipped_right'
    CLOUD = 'cloud'
    DIAMOND = 'diamond'
    ENSIGN = 'ensign'
    GURGLE = 'gurgle'
    LIGHT = 'light'
    NULL = 'null'
    OVAL = 'oval'
    PEANUT = 'peanut'
    POINTY = 'pointy'
    SLASH = 'slash'
    SQUARED = 'squared'
    STAR = 'star'
    TABBED_LEFT = 'tabbed_left'
    TABBED_RIGHT = 'tabbed_right'
    TILTED = 'tilted'
    TRAPEZOID_DOWN = 'trapezoid_down'
    TRAPEZOID_UP = 'trapezoid_up'
    WAVE = 'wave'


class HDABuilder:
    def __init__(
            self,
            name: str,
            hda_file_name: str,
            description: str,
            min_num_inputs: int,
            max_num_inputs: int,
            max_num_outputs: int,
            version: str,
            icon: str,
            hda_type: str,
            node_shape: str,
            builded_nodes,
            parameter_interface
            ):
        

        self.name = name
        self.hda_file_name = hda_file_name
        self.description = description
        self.min_num_inputs = min_num_inputs
        self.max_num_inputs = max_num_inputs
        self.version = version
        self.hda_type = hda_type
        self.node_shape = node_shape
        self.builded_nodes = builded_nodes
        self.parameter_interface = parameter_interface
        self.icon = icon
        self.max_num_outputs = max_num_outputs

        self.type_net = self._create_type_network()



        logging.debug("Creating nodes")

        hda = self.type_net.node(self.name)
        if hda:
            hda.destroy()

        placeholder = self.type_net.createNode("subnet", self.name)

        self.hda = placeholder.createDigitalAsset(
            name=self.name,
            hda_file_name=self.hda_file_name,
            description=self.description,
            min_num_inputs=self.min_num_inputs,
            max_num_inputs=self.max_num_inputs,
            version=self.version,
            ignore_external_references=True,
            create_backup=False
            )


    def _create_type_network(self) -> hou.node:
        """
        Returns:
            hou.node: Node needed for hda creation in the correct operator
        """
        node = hou.node("/obj")
        if self.hda_type == HDATypes.OBJECT:
            return node
        
        net = node.createNode(self.hda_type)
        return net

    def _link_parm(
        self,
        node: hou.Node,
        parm_name: str,
        level: int = 1,
        prepend: str = "",
        append: str = "",
    ):
        """
        Link a parameter from the source node to a destination node

        Args:
            node (hou.None): Node to add the expression to
            parm_name (str): Parameter key on the source node
            level (int): Levels between source and destination node
            prepend (str): String to prepend to source parameter key
            append (str): String to append to source parameter key
        """
        dist_name = self._parm_name(parm_name)
        org_parm = node.parmTemplateGroup().find(dist_name)
        if not org_parm:
            logging.error("parm not found: ", parm_name)
            return

        if self._is_lop and level != 1:
            level -= 1

        parm_type = "ch"
        if org_parm.dataType() == hou.parmData.String:
            parm_type = "chsop"

        if org_parm.numComponents() == 1:
            node.parm(dist_name).setExpression(
                '{}("{}{}")'.format(
                    parm_type, "../" * level, prepend + parm_name + append
                )
            )
        else:
            scheme = self._convert_naming_scheme(org_parm.namingScheme())
            for i in range(org_parm.numComponents()):
                node.parm(dist_name + scheme[i]).setExpression(
                    '{}("{}{}")'.format(
                        parm_type,
                        "../" * level,
                        prepend + parm_name + append + scheme[i],
                    )
                )

    def _link_deep_parms(
        self, node: hou.Node, parms: list[str], prepend: str = "", append: str = ""
    ):
        """
        Link a list of parameters from the source node to a destination node, including items in folders

        Args:
            node (hou.None): Node to add the expression to
            parms (list[str]): A list of parameter keys on the source node
            prepend (str): String to prepend to source parameter key
            append (str): String to append to source parameter key
        """
        for parm in parms:
            if parm.type() == hou.parmTemplateType.Folder:
                self._link_deep_parms(node, parm.parmTemplates(), prepend, append)
            else:
                self._link_parm(node, parm.name(), 2, prepend, append)

    def _set_deep_conditional(
        self,
        parms: tuple[hou.ParmTemplate, ...],
        cond_type: hou.parmCondType,
        modifier: Callable[[str], str],
    ):
        """
        Modify the conditionals of a list of parm templates

        Args:
            parms (tuple[hou.ParmTemplate, ...]): List of ParmTemplates to modify
            cond_type (hou.parmCondType): The type of conditional to modify
            modifier (Callable[[str], str]): The function which is called on the source conditional
        """
        for parm in parms:
            if parm.type() == hou.parmTemplateType.Folder:
                new_parms = self._set_deep_conditional(
                    parm.parmTemplates(), cond_type, modifier
                )
                parm.setParmTemplates(new_parms)
            elif cond_type in parm.conditionals():
                parm.setConditional(cond_type, modifier(parm.conditionals()[cond_type]))
        return parms

    def _reference_parm(
        self,
        node: hou.Node,
        dest: hou.ParmTemplateGroup,
        parm: str,
        conditional: list[hou.parmCondType, str] = None,
    ):
        """
        Create a reference of a parameter to a template group

        Args:
            node (hou.Node): The node to get the parameter from
            dest (hou.ParmTemplateGroup): The ParmTemplateGroup to add the reference to
            parm (str): The parameter key
            conditional (list[hou.parmCondType, str]): An optional conditional
        """
        org_parms = node.parmTemplateGroup()
        org_parm = org_parms.find(parm)
        if not org_parm:
            logging.error("Parm not found: ", parm)
            return

        if conditional:
            org_parm.setConditional(conditional[0], conditional[1])

        if hasattr(dest, "append"):
            dest.append(org_parm)
        elif hasattr(dest, "addParmTemplate"):
            dest.addParmTemplate(org_parm)
        else:
            logging.error("Undefined method")
            return

        self._link_parm(node, parm)

    def _rename_deep_parms(
        self, parms: list[hou.ParmTemplate], prepend: str = "", append: str = ""
    ) -> list[hou.ParmTemplate]:
        """
        Prepend and/or append a string to a list of parameter templates

        Args:
            parms (list[hou.ParmTemplate]): List of ParmTemplates to modify
            prepend (str): String to prepend to the name
            append (str): String to append to the name

        Returns:
            list[hou.ParmTemplate]: Modified list of ParmTemplates
        """
        for parm in parms:
            parm.setName(prepend + parm.name() + append)
            if parm.type() == hou.parmTemplateType.Folder:
                renamed = self._rename_deep_parms(parm.parmTemplates(), prepend, append)
                parm.setParmTemplates(renamed)
        return parms

    def _set_parm(self, node: hou.Node, parm_name: str, value: any):
        """
        Set the value of a parameter, with the context corrected name

        Args:
            node (hou.Node): Node containing parameter to modify
            parm_name (str): Name of the parameter
            value (any): Value to set parameter to
        """
        node.parm(self._parm_name(parm_name)).set(value)

    def _set_parm_expression(self, node: hou.Node, parm_name: str, value: str):
        """
        Set the value of a parameter, with the context corrected name, to an expression

        Args:
            node (hou.Node): Node containing parameter to modify
            parm_name (str): Name of the parameter
            value (str): Expression to set parameter to
        """
        node.parm(self._parm_name(parm_name)).setExpression(value)


    def build(self):
        self.hda_def = self.hda.type().definition()

        self.builded_nodes()
        self.hda_def.setParmTemplateGroup(self.parameter_interface())
        self.hda_def.setIcon(self.icon)
        if not self.max_num_outputs == 1:
            self.hda_def.setMaxNumOutputs(self.max_num_outputs)

        self.hda.setUserData('nodeshape', self.node_shape)
        self.hda_def.save(self.hda_def.libraryFilePath(), self.hda, self.hda_def.options())

        self.hda.destroy()
        self.type_net.destroy()