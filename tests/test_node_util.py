import copy
import json
from dataclasses import replace

import pytest

import cript
from cript.nodes.core import get_new_uid
from cript.nodes.exceptions import (
    CRIPTJsonNodeError,
    CRIPTJsonSerializationError,
    CRIPTNodeSchemaError,
    CRIPTOrphanedComputationalProcessError,
    CRIPTOrphanedComputationError,
    CRIPTOrphanedDataError,
    CRIPTOrphanedMaterialError,
    CRIPTOrphanedProcessError,
)
from tests.utils.util import strip_uid_from_dict


def test_removing_nodes(simple_algorithm_node, complex_parameter_node, simple_algorithm_dict):
    a = simple_algorithm_node
    p = complex_parameter_node
    a.parameter += [p]
    assert strip_uid_from_dict(json.loads(a.json)) != simple_algorithm_dict
    a.remove_child(p)
    assert strip_uid_from_dict(json.loads(a.json)) == simple_algorithm_dict


def test_uid_deserialization(simple_algorithm_node, complex_parameter_node, simple_algorithm_dict):
    identifier = [{"bigsmiles": "123456"}]
    material = cript.Material(name="my material", identifier=identifier)

    computation = cript.Computation(name="my computation name", type="analysis")
    property1 = cript.Property("modulus_shear", "value", 5.0, "GPa", computation=[computation])
    property2 = cript.Property("modulus_loss", "value", 5.0, "GPa", computation=[computation])
    material.property = [property1, property2]

    material2 = cript.load_nodes_from_json(material.json)
    assert json.loads(material.json) == json.loads(material2.json)

    material3_dict = {
        "node": ["Material"],
        "uid": "_:f6d56fdc-9df7-49a1-a843-cf92681932ad",
        "uuid": "f6d56fdc-9df7-49a1-a843-cf92681932ad",
        "name": "my material",
        "property": [
            {
                "node": ["Property"],
                "uid": "_:82e7270e-9f35-4b35-80a2-faa6e7f670be",
                "uuid": "82e7270e-9f35-4b35-80a2-faa6e7f670be",
                "key": "modulus_shear",
                "type": "value",
                "value": 5.0,
                "unit": "GPa",
                "computation": [{"uid": "_:9ddda2c0-ff8c-4ce3-beb0-e0cafb6169ef"}],
            },
            {
                "node": ["Property"],
                "uid": "_:fc4dfa5e-742c-4d0b-bb66-2185461f4582",
                "uuid": "fc4dfa5e-742c-4d0b-bb66-2185461f4582",
                "key": "modulus_loss",
                "type": "value",
                "value": 5.0,
                "unit": "GPa",
                "computation": [
                    {
                        "uid": "_:9ddda2c0-ff8c-4ce3-beb0-e0cafb6169ef",
                    }
                ],
            },
        ],
        "bigsmiles": "123456",
    }

    with pytest.raises(cript.nodes.exceptions.CRIPTDeserializationUIDError):
        cript.load_nodes_from_json(json.dumps(material3_dict))

    # TODO convince beartype to allow _ProxyUID as well
    # material4_dict = {
    #     "node": [
    #         "Material"
    #     ],
    #     "uid": "_:f6d56fdc-9df7-49a1-a843-cf92681932ad",
    #     "uuid": "f6d56fdc-9df7-49a1-a843-cf92681932ad",
    #     "name": "my material",
    #     "property": [
    #         {
    #             "node": [
    #                 "Property"
    #             ],
    #             "uid": "_:82e7270e-9f35-4b35-80a2-faa6e7f670be",
    #             "uuid": "82e7270e-9f35-4b35-80a2-faa6e7f670be",
    #             "key": "modulus_shear",
    #             "type": "value",
    #             "value": 5.0,
    #             "unit": "GPa",
    #             "computation": [
    #                 {
    #                     "node": [
    #                         "Computation"
    #                     ],
    #                     "uid": "_:9ddda2c0-ff8c-4ce3-beb0-e0cafb6169ef"
    #                 }
    #             ]
    #         },
    #         {
    #             "node": [
    #                 "Property"
    #             ],
    #             "uid": "_:fc4dfa5e-742c-4d0b-bb66-2185461f4582",
    #             "uuid": "fc4dfa5e-742c-4d0b-bb66-2185461f4582",
    #             "key": "modulus_loss",
    #             "type": "value",
    #             "value": 5.0,
    #             "unit": "GPa",
    #             "computation": [
    #                 {
    #                     "node": [
    #                         "Computation"
    #                     ],
    #                     "uid": "_:9ddda2c0-ff8c-4ce3-beb0-e0cafb6169ef",
    #                     "uuid": "9ddda2c0-ff8c-4ce3-beb0-e0cafb6169ef",
    #                     "name": "my computation name",
    #                     "type": "analysis",
    #                     "citation": []
    #                 }
    #             ]
    #         }
    #     ],
    #     "bigsmiles": "123456"
    # }

    # material4 = cript.load_nodes_from_json(json.dumps(material4_dict))
    # assert json.loads(material.json) == json.loads(material4.json)


def test_json_error(complex_parameter_node):
    parameter = complex_parameter_node
    # Let's break the node by violating the data model
    parameter._json_attrs = replace(parameter._json_attrs, value="abc")
    with pytest.raises(CRIPTNodeSchemaError):
        parameter.validate()
    # Let's break it completely
    parameter._json_attrs = None
    with pytest.raises(CRIPTJsonSerializationError):
        parameter.json


def test_local_search(simple_algorithm_node, complex_parameter_node):
    a = simple_algorithm_node
    # Check if we can use search to find the algorithm node, but specifying node and key
    find_algorithms = a.find_children({"node": "Algorithm", "key": "mc_barostat"})
    assert find_algorithms == [a]
    # Check if it correctly exclude the algorithm if key is specified to non-existent value
    find_algorithms = a.find_children({"node": "Algorithm", "key": "mc"})
    assert find_algorithms == []

    # Adding 2 separate parameters to test deeper search
    p1 = complex_parameter_node
    p2 = copy.deepcopy(complex_parameter_node)
    p2.key = "damping_time"
    p2.value = 15.0
    p2.unit = "m"
    a.parameter += [p1, p2]

    # Test if we can find a specific one of the parameters
    find_parameter = a.find_children({"key": "damping_time"})
    assert find_parameter == [p2]

    # Test to find the other parameter
    find_parameter = a.find_children({"key": "update_frequency"})
    assert find_parameter == [p1]

    # Test if correctly find no parameter if we are searching for a non-existent parameter
    find_parameter = a.find_children({"key": "update"})
    assert find_parameter == []

    # Test nested search. Here we are looking for any node that has a child node parameter as specified.
    find_algorithms = a.find_children({"parameter": {"key": "damping_time"}})
    assert find_algorithms == [a]
    # Same as before, but specifying two children that have to be present (AND condition)
    find_algorithms = a.find_children({"parameter": [{"key": "damping_time"}, {"key": "update_frequency"}]})
    assert find_algorithms == [a]

    # Test that the main node is correctly excluded if we specify an additionally non-existent parameter
    find_algorithms = a.find_children({"parameter": [{"key": "damping_time"}, {"key": "update_frequency"}, {"foo": "bar"}]})
    assert find_algorithms == []


def test_cycles(complex_data_node, simple_computation_node):
    # We create a wrong cycle with parameters here.
    # TODO replace this with nodes that actually can form a cycle
    d = copy.deepcopy(complex_data_node)
    c = copy.deepcopy(simple_computation_node)
    d.computation += [c]
    # Using input and output data guarantees a cycle here.
    c.output_data += [d]
    c.input_data += [d]

    # # Test the repetition of a citation.
    # # Notice that we do not use a deepcopy here, as we want the citation to be the exact same node.
    # citation = d.citation[0]
    # # c._json_attrs.citation.append(citation)
    # c.citation += [citation]
    # # print(c.get_json(indent=2).json)
    # # c.validate()

    # Generate json with an implicit cycle
    c.json
    d.json


def test_uid_serial(simple_inventory_node):
    simple_inventory_node.material += simple_inventory_node.material
    json_dict = json.loads(simple_inventory_node.get_json(condense_to_uuid={}).json)
    assert len(json_dict["material"]) == 4
    assert isinstance(json_dict["material"][2]["uid"], str)
    assert json_dict["material"][2]["uid"].startswith("_:")
    assert len(json_dict["material"][2]["uid"]) == len(get_new_uid())
    assert isinstance(json_dict["material"][3]["uid"], str)
    assert json_dict["material"][3]["uid"].startswith("_:")
    assert len(json_dict["material"][3]["uid"]) == len(get_new_uid())
    assert json_dict["material"][3]["uid"] != json_dict["material"][2]["uid"]


def test_invalid_json_load():
    def raise_node_dict(node_dict):
        node_str = json.dumps(node_dict)
        with pytest.raises(CRIPTJsonNodeError):
            cript.load_nodes_from_json(node_str)

    node_dict = {"node": "Computation"}
    raise_node_dict(node_dict)
    node_dict = {"node": []}
    raise_node_dict(node_dict)
    node_dict = {"node": ["asdf", "asdf"]}
    raise_node_dict(node_dict)
    node_dict = {"node": [None]}
    raise_node_dict(node_dict)


def test_invalid_project_graphs(simple_project_node, simple_material_node, simple_process_node, simple_property_node, simple_data_node, simple_computation_node, simple_computation_process_node):
    project = copy.deepcopy(simple_project_node)
    process = copy.deepcopy(simple_process_node)
    material = copy.deepcopy(simple_material_node)

    ingredient = cript.Ingredient(material=material, quantity=[cript.Quantity(key="mass", value=1.23, unit="kg")])
    process.ingredient += [ingredient]

    # Add the process to the experiment, but not in inventory or materials
    # Invalid graph
    project.collection[0].experiment[0].process += [process]
    with pytest.raises(CRIPTOrphanedMaterialError):
        project.validate()

    # First fix add material to inventory
    project.collection[0].inventory += [cript.Inventory("test_inventory", material=[material])]
    project.validate()
    # Reverse this fix
    project.collection[0].inventory = []
    with pytest.raises(CRIPTOrphanedMaterialError):
        project.validate()

    # Fix by add to the materials list instead.
    # Using the util helper function for this.
    cript.add_orphaned_nodes_to_project(project, active_experiment=None, max_iteration=10)
    project.validate()

    # Now add an orphan process to the graph
    process2 = copy.deepcopy(simple_process_node)
    process.prerequisite_process += [process2]
    with pytest.raises(CRIPTOrphanedProcessError):
        project.validate()

    # Wrong fix it helper node
    dummy_experiment = copy.deepcopy(project.collection[0].experiment[0])
    with pytest.raises(RuntimeError):
        cript.add_orphaned_nodes_to_project(project, dummy_experiment)
    # Problem still persists
    with pytest.raises(CRIPTOrphanedProcessError):
        project.validate()
    # Fix by using the helper function correctly
    cript.add_orphaned_nodes_to_project(project, project.collection[0].experiment[0], 10)
    project.validate()

    # We add property to the material, because that adds the opportunity for orphaned data and computation
    property = copy.deepcopy(simple_property_node)
    material.property += [property]
    project.validate()
    # Now add an orphan data
    data = copy.deepcopy(simple_data_node)
    property.data = [data]
    with pytest.raises(CRIPTOrphanedDataError):
        project.validate()
    # Fix with the helper function
    cript.add_orphaned_nodes_to_project(project, project.collection[0].experiment[0], 10)
    project.validate()

    # Add an orphan Computation
    computation = copy.deepcopy(simple_computation_node)
    property.computation += [computation]
    with pytest.raises(CRIPTOrphanedComputationError):
        project.validate()
    # Fix with the helper function
    cript.add_orphaned_nodes_to_project(project, project.collection[0].experiment[0], 10)
    project.validate()

    # Add orphan computational process
    comp_proc = copy.deepcopy(simple_computation_process_node)
    data.computation_process += [comp_proc]
    with pytest.raises(CRIPTOrphanedComputationalProcessError):
        while True:
            try:  # Do trigger not orphan materials
                project.validate()
            except CRIPTOrphanedMaterialError as exc:
                project._json_attrs.material.append(exc.orphaned_node)
            except CRIPTOrphanedProcessError as exc:
                project.collection[0].experiment[0]._json_attrs.process.append(exc.orphaned_node)
            else:
                break

    cript.add_orphaned_nodes_to_project(project, project.collection[0].experiment[0], 10)
    project.validate()


def test_expanded_json(complex_project_node):
    """
    Tests the generation and deserialization of expanded JSON for a complex project node.

    This test verifies 2 key aspects:
        1. A complex project node can be serialized into an expanded JSON string, without UUID placeholders.
        2. The expanded JSON can be deserialized into a node  that is equivalent to the original node.
    """
    project_expanded_json: str = complex_project_node.get_expanded_json()
    deserialized_project_node: cript.Project = cript.load_nodes_from_json(project_expanded_json)

    # assert the expanded JSON was correctly deserialized to project node
    assert deserialized_project_node == complex_project_node

    condensed_json: str = complex_project_node.json

    # since short JSON has UUID it will not be able to deserialize correctly and will
    # raise CRIPTJsonDeserializationError
    with pytest.raises(cript.nodes.exceptions.CRIPTJsonDeserializationError):
        cript.load_nodes_from_json(condensed_json)
