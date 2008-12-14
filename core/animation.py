"""functions related to animation"""

import pymel.util as util
import factories as _factories
import general

import pmcmds as cmds
#import maya.cmds as cmds
import maya.mel as mm


def currentTime( *args, **kwargs ):
    """
Modifications:
    - if no args are provided, the command returns the current time -- the equivalent of::
    
        >>> cmds.currentTime(q=1)
    """
    
    if not args and not kwargs:
        return cmds.currentTime(q=1)
    else:
        return cmds.currentTime(*args, **kwargs)
    
def getCurrentTime():
    """get the current time as a float"""
    return cmds.currentTime(q=1)
    
def setCurrentTime( time ):
    """set the current time """
    return cmds.currentTime(time) 

def listAnimatable( *args, **kwargs ):
    """
Modifications:
    - returns an empty list when the result is None
    - returns wrapped classes
    """
    return map( general.PyNode, util.listForNone(cmds.listAnimatable( *args, **kwargs ) ) )


def deformer(*args, **kwargs):
    return map( PyNode, cmds.deformer(*args, **kwargs) )
    
def joint(*args, **kwargs):
    """
Maya Bug Fix:
    - when queried, limitSwitch*, stiffness*, and angle* flags returned lists of values instead 
        of single values. Values are now properly unpacked
    """
    
    res = cmds.joint(*args, **kwargs)
    
    #if kwargs.pop('query',False) or kwargs.pop('q',False):

    if kwargs.get('query', kwargs.get( 'q', False)):
        args = [
        'limitSwitchX', 'lsx',
        'limitSwitchY', 'lsy',
        'limitSwitchZ', 'lsz',
        'stiffnessX', 'stx',
        'stiffnessY', 'sty',
        'stiffnessZ', 'stz',
        'angleX', 'ax',
        'angleY', 'ay',
        'angleZ', 'az'
        ]
        if filter( lambda x: x in args, kwargs.keys()):
            res = res[0]
    elif res is not None:    
        res = general.PyNode(res)
    return res

def _constraint( func ):

    def constraint(*args, **kwargs):
        """
Maya Bug Fix:
    - when queried, upVector, worldUpVector, and aimVector returned the name of the constraint instead of the desired values
Modifications:
    - added new syntax for querying the weight of a target object, by passing the constraint first::
    
        aimConstraint( 'pCube1_aimConstraint1', q=1, weight ='pSphere1' )
        aimConstraint( 'pCube1_aimConstraint1', q=1, weight =['pSphere1', 'pCylinder1'] )
        aimConstraint( 'pCube1_aimConstraint1', q=1, weight =[] )
        """
        if kwargs.get( 'query', kwargs.get('q', False) and len(args)==1) :
            
            # Fix the big with upVector, worldUpVector, and aimVector
            attrs = [
            'upVector', 'u',
            'worldUpVector', 'wu',
            'aimVector', 'a' ]
            
            for attr in attrs:
                if attr in kwargs:
                    return general.Vector( general.getAttr(args[0] + "." + attr ) )
            
            # ...otherwise, try seeing if we can apply the new weight query syntax
            targetObjects =  kwargs.get( 'weight', kwargs.get('w', None) )
            if targetObjects is not None: 
                # old way caused KeyError if 'w' not in kwargs, even if 'weight' was!
                # targetObjects = kwargs.get( 'weight', kwargs['w'] )
                constraint = args[0]
                if 'constraint' in cmds.nodeType( constraint, inherited=1 ):
                    if not util.isIterable( targetObjects ):
                        targetObjects = [targetObjects]
                    elif not targetObjects:
                        targetObjects = func( constraint, q=1, targetList=1 )
    
                    constraintObj = cmds.listConnections( constraint + '.constraintParentInverseMatrix', s=1, d=0 )[0]    
                    args = targetObjects + [constraintObj]
                    kwargs.pop('w',None)
                    kwargs['weight'] = True
                
        res = func(*args, **kwargs)
        return res
    
    constraint.__name__ = func.__name__
    return constraint

aimConstraint = _constraint( cmds.aimConstraint )
geometryConstraint = _constraint( cmds.geometryConstraint )
normalConstraint = _constraint( cmds.normalConstraint )
orientConstraint = _constraint( cmds.orientConstraint )
pointConstraint = _constraint( cmds.pointConstraint )
scaleConstraint = _constraint( cmds.scaleConstraint )

_factories.createFunctions( __name__, general.PyNode )

