from ploneid import PloneIdCooker, manage_addPloneIdCooker
from etal import EtalIdCooker, manage_addEtalIdCooker
from abbrev import AbbrevIdCooker, manage_addAbbrevIdCooker
from uid import UidIdCooker, manage_addUidIdCooker

def initialize(context):
    context.registerClass(PloneIdCooker,
                          constructors = (manage_addPloneIdCooker,),
                          )
    context.registerClass(EtalIdCooker,
                          constructors = (manage_addEtalIdCooker,),
                          )
    context.registerClass(AbbrevIdCooker,
                          constructors = (manage_addAbbrevIdCooker,),
                          )
    context.registerClass(UidIdCooker,
                          constructors = (manage_addUidIdCooker,),
                          )
