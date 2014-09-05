

def get_entity_base_instanse_by_id_and_type(entity_id, entity_type):
    from spudderaccounts.wrappers import RoleBase
    from spudderdomain.controllers import RoleController, EntityController
    from spudderdomain.wrappers import EntityBase
    if entity_type in RoleController.ENTITY_TYPES:
        entity = RoleController.GetRoleForEntityTypeAndID(
            entity_type, entity_id,
            RoleBase.RoleWrapperByEntityType(entity_type))
    elif entity_type in EntityController.ENTITY_TYPES:
        entity = EntityController.GetWrappedEntityByTypeAndId(
            entity_type, entity_id,
            EntityBase.EntityWrapperByEntityType(entity_type))
    else:
        raise NotImplementedError("Entity type %s is not supported" % entity_type)
    return entity
