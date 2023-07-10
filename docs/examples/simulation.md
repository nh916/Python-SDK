---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

!!! abstract
    This tutorial guides you through an example material synthesis workflow using the
    [CRIPT Python SDK](https://pypi.org/project/cript/).


## Installation

Before you start, be sure the [cript python package](https://pypi.org/project/cript/) is installed.

```bash
pip install cript
```

## Connect to CRIPT

To connect to CRIPT, you must enter a `host` and an `API Token`. For most users, `host` will be `https://criptapp.org`.

!!! Warning "Keep API Token Secure"

    To ensure security, avoid storing sensitive information like tokens directly in your code.
    Instead, use environment variables.
    Storing tokens in code shared on platforms like GitHub can lead to security incidents.
    Anyone that possesses your token can impersonate you on the [CRIPT](https://criptapp.org/) platform.
    Consider [alternative methods for loading tokens with the CRIPT API Client](https://c-accel-cript.github.io/Python-SDK/api/api/#cript.api.api.API.__init__).
    In case your token is exposed be sure to immediately generate a new token to revoke the access of the old one
    and keep the new token safe.

```python
import cript

with cript.API(host="http://development.api.mycriptapp.org/", token="123456") as api:
    pass
```

!!! note

    You may notice, that we are not executing any code inside the context manager block.
    If you were to write a python script, compared to a jupyter notebook, you would add all the following code inside that block.
    Here in a jupyter notebook, we need to connect manually. We just have to remember to disconnect at the end.

```python
api = cript.API(host="http://development.api.mycriptapp.org/", token=None)
api = api.connect()
```

## Create a Project

All data uploaded to CRIPT must be associated with a [project](../../nodes/primary_nodes/project) node.
[Project](../../nodes/primary_nodes/project) can be thought of as an overarching research goal.
For example, finding a replacement for an existing material from a sustainable feedstock.

```python
# create a new project in the CRIPT database
project = cript.Project(name="My simulation project.")
```

## Create a Collection node

For this project, you can create multiple collections, which represent a set of experiments.
For example, you can create a collection for a specific manuscript,
or you can create a collection for initial screening of candidates and one for later refinements etc.

So, let's create a collection node and add it to the project.

```python
collection = cript.Collection(name="Initial simulation screening")
# We add this collection to the project as a list.
project.collection += [collection]
```

!!! note "Viewing CRIPT JSON"

    Note, that if you are interested into the inner workings of CRIPT,
    you can obtain a JSON representation of your data graph at any time to see what is being sent to the API.

```python
print(project.json)
print("\nOr more pretty\n")
print(project.get_json(indent=2).json)
```

## Create an Experiment node

The [collection node](../../nodes/primary_nodes/collection) holds a series of
[Experiment nodes](../../nodes/primary_nodes/experiment) nodes.

And we can add this experiment to the collection of the project.

```python
experiment = cript.Experiment(name="Simulation for the first candidate")
collection.experiment += [experiment]
```

# Create relevant Software nodes

[Software](../../nodes/subobjects/software) nodes refer to software that you use during your simulation experiment.
In general `Software` nodes can be shared between project, and it is encouraged to do so if the software you are using is already present in the CRIPT project use it.

If They are not, you can create them as follows:

```python
python = cript.Software(name="python", version="3.9")
rdkit = cript.Software(name="rdkit", version="2020.9")
stage = cript.Software(name="stage", source="https://doi.org/10.1021/jp505332p", version="N/A")
packmol = cript.Software(name="Packmol", source="http://m3g.iqm.unicamp.br/packmol", version="N/A")
openmm = cript.Software(name="openmm", version="7.5")
```

Generally, provide as much information about the software as possible this helps to make your results reproducible.
Even a software is not publicly available, like an in-house code, we encourage you to specify them in CRIPT.
If a version is not available, consider using git-hashes.



# Create Software Configurations

Now that we have our <a href="../../nodes/software" target="_blank">`Software`</a> nodes, we can create <a href="../../subobjects/software_configuration" target="_blank">`SoftwareConfiguration`</a> nodes.
`SoftwareConfiguration` nodes are designed to let you specify details, about which algorithms from the software package you are using and log parameters for these algorithms.

The `SoftwareConfigurations` are then used for constructing our <a href="../../nodes/computation" target="_blank">`Computation`</a> node, which describe the actual computation you are performing.

We can also attach <a href="../../subobjects/algorithm" target="_blank">`Algorithm`</a> nodes to a <a href="../../subobjects/software_configuration" target="_blank">`SoftwareConfiguration`</a> node. The <a href="../../subobjects/algorithm" target="_blank">`Algorithm`</a> nodes may contain nested <a href="../../subobjects/parameter" target="_blank">`Parameter`</a> nodes, as shown in the example below.



```python
# create some software configuration nodes
python_config = cript.SoftwareConfiguration(software=python)
rdkit_config = cript.SoftwareConfiguration(software=rdkit)
stage_config = cript.SoftwareConfiguration(software=stage)

# create a software configuration node with a child Algorithm node
openmm_config = cript.SoftwareConfiguration(
    software=openmm,
    algorithm=[
        cript.Algorithm(
            key="energy_minimization",
            type="initialization",
        ),
    ],
)
packmol_config = cript.SoftwareConfiguration(software=packmol)
```

!!! note "Algorithm keys"
    The allowed `Algorithm` keys are listed under <a href="https://criptapp.org/keys/algorithm-key/" target="_blank">algorithm keys</a> in the CRIPT controlled vocabulary.

!!! note "Parameter keys"
    The allowed `Parameter` keys are listed under <a href="https://criptapp.org/keys/parameter-key/" target="_blank">parameter keys</a> in the CRIPT controlled vocabulary.


# Create Computations

Now that we've created some <a href="../../subobjects/software_configuration" target="_blank">`SoftwareConfiguration`</a> nodes, we can used them to build full <a href="../../nodes/computation" target="_blank">`Computation`</a> nodes.
In some cases, we may also want to add <a href="../../subobjects/condition" target="_blank">`Condition`</a> nodes to our computation, to specify the conditions at which the computation was carried out. An example of this is shown below.


```python
# Create a ComputationNode
# This block of code represents the computation involved in generating forces.
# It also details the initial placement of molecules within a simulation box.
init = cript.Computation(
    name="Initial snapshot and force-field generation",
    type="initialization",
    software_configuration=[
        python_config,
        rdkit_config,
        stage_config,
        packmol_config,
        openmm_config,
    ],
)

# Initiate the simulation equilibration using a separate node.
# The equilibration process is governed by specific conditions and a set equilibration time.
# Given this is an NPT (Number of particles, Pressure, Temperature) simulation, conditions such as the number of chains, temperature, and pressure are specified.
equilibration = cript.Computation(
    name="Equilibrate data prior to measurement",
    type="MD",
    software_configuration=[python_config, openmm_config],
    condition=[
        cript.Condition(key="time_duration", type="value", value=100.0, unit="ns"),
        cript.Condition(key="temperature", type="value", value=450.0, unit="K"),
        cript.Condition(key="pressure", type="value", value=1.0, unit="bar"),
        cript.Condition(key="number", type="value", value=31),
    ],
    prerequisite_computation=init,
)

# This section involves the actual data measurement.
# Note that we use the previously computed data as a prerequisite. Additionally, we incorporate the input data at a later stage.
bulk = cript.Computation(
    name="Bulk simulation for measurement",
    type="MD",
    software_configuration=[python_config, openmm_config],
    condition=[
        cript.Condition(key="time_duration", type="value", value=50.0, unit="ns"),
        cript.Condition(key="temperature", type="value", value=450.0, unit="K"),
        cript.Condition(key="pressure", type="value", value=1.0, unit="bar"),
        cript.Condition(key="number", type="value", value=31),
    ],
    prerequisite_computation=equilibration,
)

# The following step involves analyzing the data from the measurement run to ascertain a specific property.
ana = cript.Computation(
    name="Density analysis",
    type="analysis",
    software_configuration=[python_config],
    prerequisite_computation=bulk,
)

# Add all these computations to the experiment.
experiment.computation += [init, equilibration, bulk, ana]
```


!!! note "Computation types"
    The allowed `Computation` types are listed under <a href="https://criptapp.org/keys/computation-type/" target="_blank">computation types</a> in the CRIPT controlled vocabulary.

!!! note "Condition keys"
    The allowed `Condition` keys are listed under <a href="https://criptapp.org/keys/condition-key/" target="_blank">condition keys</a> in the CRIPT controlled vocabulary.


# Create and Upload Files

New we'd like to upload files associated with our simulation. First, we'll instantiate our File nodes under a specific project.

```python
packing_file = cript.File("Initial simulation box snapshot with roughly packed molecules", type="computation_snapshot", source="path/to/local/file")
forcefield_file = cript.File(name="Forcefield definition file", type="data", source="path/to/local/file")
snap_file = cript.File("Bulk measurement initial system snap shot", type="computation_snapshot", source="path/to/local/file")
final_file = cript.File("Final snapshot of the system at the end the simulations", type="computation_snapshot", source="path/to/local/file")
```

!!! note
The `source` field should point to any file on your local filesystem.

!!! info
Depending on the file size, there could be a delay while the checksum is generated.

Note, that we haven't uploaded the files to CRIPT yet, this is automatically performed, when the project is uploaded via `api.save(project)`.


# Create Data

Next, we'll create a <a href="../../nodes/data" target="_blank">`Data`</a> node which helps organize our <a href="../../nodes/file" target="_blank">`File`</a> nodes and links back to our <a href="../../nodes/computation" target="_blank">`Computation`</a> objects.

```python
packing_data = cript.Data(
    name="Loosely packed chains",
    type="computation_config",
    file=[packing_file],
    computation=[init],
    notes="PDB file without topology describing an initial system.",
)

forcefield_data = cript.Data(
    name="OpenMM forcefield",
    type="computation_forcefield",
    file=[forcefield_file],
    computation=[init],
    notes="Full forcefield definition and topology.",
)

equilibration_snap = cript.Data(
    name="Equilibrated simulation snapshot",
    type="computation_config",
    file=[snap_file],
    computation=[equilibration],
)

final_data = cript.Data(
    name="Logged volume during simulation",
    type="computation_trajectory",
    file=[final_file],
    computation=[bulk],
)
```

!!! note "Data types"
    The allowed `Data` types are listed under the <a href="https://criptapp.org/keys/data-type/" target="_blank">data types</a> in the CRIPT controlled vocabulary.

Next, we'll link these <a href="../../nodes/data" target="_blank">`Data`</a> nodes to the appropriate <a href="../../nodes/computation" target="_blank">`Computation`</a> nodes.

```python

# Observe how this step also forms a continuous graph, enabling data to flow from one computation to the next.
# The sequence initiates with the computation process and culminates with the determination of the material property.
init.output_data = [packing_data, forcefield_data]
equilibration.input_data = [packing_data, forcefield_data]
equilibration.output_data = [equilibration_snap]
ana.input_data = [final_data]
bulk.output_data = [final_data]
```

# Create a virtual Material

Finally, we'll create a virtual material and link it to the <a href="../../nodes/computation" target="_blank">`Computation`</a> nodes that we've built.

```py

```

Next, let's add some [`Identifier`](../subobjects/identifier.md) nodes to the material to make it easier to identify and search.

```py
names = cript.Identifier(
    key="names",
    value=["poly(styrene)", "poly(vinylbenzene)"],
)

bigsmiles = cript.Identifier(
    key="bigsmiles",
    value="[H]{[>][<]C(C[>])c1ccccc1[<]}C(C)CC",
)

chem_repeat = cript.Identifier(
    key="chem_repeat",
    value="C8H8",
)

polystyrene.add_identifier(names)
polystyrene.add_identifier(chem_repeat)
polystyrene.add_identifier(bigsmiles)
```

!!! note "Identifier keys"
    The allowed `Identifier` keys are listed in the <a href="https://criptapp.org/keys/material-identifier-key/" target="_blank">material identifier keys</a> in the CRIPT controlled vocabulary.

Let's also add some [`Property`](../subobjects/property.md) nodes to the `Material`, which represent its physical or virtual (in the case of a simulated material) properties.

```py
phase = cript.Property(key="phase", value="solid")
color = cript.Property(key="color", value="white")

polystyrene.add_property(phase)
polystyrene.add_property(color)
```

!!! note "Material property keys"
    The allowed material `Property` keys are listed in the <a href="https://criptapp.org/keys/material-property-key/" target="_blank">material property keys</a> in the CRIPT controlled vocabulary.

```python
identifiers = [{"names": ["poly(styrene)", "poly(vinylbenzene)"]}]
identifiers += [{"bigsmiles": "[H]{[>][<]C(C[>])c1ccccc1[<]}C(C)CC"}]
identifiers += [{"chem_repeat": ["C8H8"]}]

polystyrene = cript.Material(name="virtual polystyrene", identifiers=identifiers)
```

Finally, we'll create a [`ComputationalForcefield`](../subobjects/computational_forcefield.md) node and link it to the Material.


```python
forcefield = cript.ComputationalForcefield(
    key="opls_aa",
    building_block="atom",
    source="Custom determination via STAGE",
    data=[forcefield_data],
)

polystyrene.computational_forcefield = forcefield
```

!!! note "Computational forcefield keys"
    The allowed `ComputationalForcefield` keys are listed under the <a href="https://criptapp.org/keys/computational-forcefield-key/" target="_blank">computational forcefield keys</a> in the CRIPT controlled vocabulary.

Now we can save the project to CRIPT (and upload the files) or inspect the JSON output

```python
# Before we can save it, we should add all the orphaned nodes to the experiments.
# It is important to do this for every experiment separately, but here we only have one.
cript.add_orphaned_nodes_to_project(project, active_experiment=experiment)
project.validate()

# api.save(project)
print(project.get_json(indent=2).json)

# Let's not forget to close the API connection after everything is done.
api.disconnect()
```

# Conclusion

You made it! We hope this tutorial has been helpful.

Please let us know how you think it could be improved.
Feel free to reach out to us on our [CRIPT Python SDK GitHub](https://github.com/C-Accel-CRIPT/Python-SDK).
We'd love your inputs and contributions!