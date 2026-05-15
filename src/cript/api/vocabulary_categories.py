from enum import Enum


class VocabCategories(Enum):
    """
    All available [CRIPT controlled vocabulary categories](https://app.criptapp.org/vocab/)

    Controlled vocabulary categories are used to classify data.

    Attributes
    ----------
    ALGORITHM_KEY: str
        Algorithm key.
    ALGORITHM_TYPE: str
        Algorithm type.
    BUILDING_BLOCK: str
        Building block.
    CITATION_TYPE: str
        Citation type.
    COMPUTATION_TYPE: str
       Computation type.
    COMPUTATIONAL_FORCEFIELD_KEY: str
        Computational forcefield key.
    COMPUTATIONAL_PROCESS_PROPERTY_KEY: str
        Computational process property key.
    COMPUTATIONAL_PROCESS_TYPE: str
        Computational process type.
    CONDITION_KEY: str
        Condition key.
    DATA_LICENSE: str
        Data license.
    DATA_TYPE: str
        Data type.
    EQUIPMENT_KEY: str
        Equipment key.
    FILE_TYPE: str
        File type.
    INGREDIENT_KEYWORD: str
        Ingredient keyword.
    MATERIAL_IDENTIFIER_KEY: str
        Material identifier key.
    MATERIAL_KEYWORD: str
        Material keyword.
    MATERIAL_PROPERTY_KEY: str
        Material property key.
    PARAMETER_KEY: str
        Parameter key.
    PROCESS_KEYWORD: str
        Process keyword.
    PROCESS_PROPERTY_KEY: str
        Process property key.
    PROCESS_TYPE: str
        Process type.
    PROPERTY_METHOD: str
        Property method.
    QUANTITY_KEY: str
        Quantity key.
    REFERENCE_TYPE: str
        Reference type.
    SET_TYPE: str
        Set type.
    UNCERTAINTY_TYPE: str
        Uncertainty type.

    Examples
    --------
    >>> import cript
    >>> algorithm_vocabulary = api.get_vocab_by_category(
    ...     cript.VocabCategories.ALGORITHM_KEY
    ... )
    """

    ALGORITHM_KEY = "algorithm_key"
    ALGORITHM_TYPE = "algorithm_type"
    BUILDING_BLOCK = "building_block"
    CITATION_TYPE = "citation_type"
    COMPUTATION_TYPE = "computation_type"
    COMPUTATIONAL_FORCEFIELD_KEY = "computational_forcefield_key"
    COMPUTATIONAL_PROCESS_PROPERTY_KEY = "computational_process_property_key"
    COMPUTATIONAL_PROCESS_TYPE = "computational_process_type"
    CONDITION_KEY = "condition_key"
    DATA_LICENSE = "data_license"
    DATA_TYPE = "data_type"
    EQUIPMENT_KEY = "equipment_key"
    FILE_TYPE = "file_type"
    INGREDIENT_KEYWORD = "ingredient_keyword"
    MATERIAL_IDENTIFIER_KEY = "material_identifier_key"
    MATERIAL_KEYWORD = "material_keyword"
    MATERIAL_PROPERTY_KEY = "material_property_key"
    PARAMETER_KEY = "parameter_key"
    PROCESS_KEYWORD = "process_keyword"
    PROCESS_PROPERTY_KEY = "process_property_key"
    PROCESS_TYPE = "process_type"
    PROPERTY_METHOD = "property_method"
    QUANTITY_KEY = "quantity_key"
    REFERENCE_TYPE = "reference_type"
    SET_TYPE = "set_type"
    UNCERTAINTY_TYPE = "uncertainty_type"
