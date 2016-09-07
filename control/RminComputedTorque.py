# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 14:59:30 2016

@author: alex
"""

from AlexRobotics.dynamic  import Hybrid_Manipulator   as HM
from AlexRobotics.control  import ComputedTorque       as CTC


import numpy as np


'''
################################################################################
'''

    
class RminComputedTorqueController( CTC.ComputedTorqueController ):
    """ Feedback law  """
    ############################
    def __init__( self , R = HM.HybridTwoLinkManipulator() ):
        """ """
        
        CTC.ComputedTorqueController.__init__( self , R  )
        
        self.n_gears = 4
        
        self.hysteresis       = False
        self.hys_level        = 1
        self.last_gear_i      = 1 # Default gear
        
        
    ############################
    def traj_following_ctl( self , x , t ):
        """ 
        
        Given desired loaded trajectory and actual state, compute torques and optimal gear ratio
        
        """
        
        ddq_d , dq_d , q_d = self.get_traj( t )

        ddq_r              = self.compute_ddq_r( ddq_d , dq_d , q_d , x )
        
        u                  = self.u_star( ddq_r , x )
        
        return u
        
        
    ############################
    def fixed_goal_ctl( self , x , t = 0 ):
        """ 
        
        Given desired fixed goal state and actual state, compute torques and optimal gear ratio
        
        """
        
        ddq_d          =   np.zeros( self.R.dof )

        [ q_d , dq_d ] = self.R.x2q( self.goal  )   # from state vector (x) to angle and speeds (q,dq)

        ddq_r          = self.compute_ddq_r( ddq_d , dq_d , q_d , x )
        
        u              = self.u_star( ddq_r , x )
        
        return u
        
        
    ############################
    def manual_acc_ctl( self , x , t = 0 ):
        """ 
        
        Given desired acc, compute torques and optimal gear ratio
        
        """

        ddq_r          = self.ddq_manual_setpoint
        
        u              = self.u_star( ddq_r , x )
        
        return u
        
    
    ############################
    def u_star( self , ddq_r , x  ):
        """ 
        
        Compute optimal u given desired accel and actual states
        
        """
        
        # Cost is Q
        Q = np.zeros( self.n_gears )
        T = np.zeros( ( self.n_gears , self.R.dof ) )
        
        #for all gear ratio options
        for i in xrange( self.n_gears ):
            
            T[i] = self.computed_torque( ddq_r , x , self.uD(i) ) 
            
            # Cost is norm of torque
            #Q[i] = np.dot( T[i] , T[i] )
            
            # Verify validity
            u_test  = np.append( T[i] , self.uD(i) )
            
            if self.R.isavalidinput( x , u_test ):
                # valid option
                
                # Cost is norm of torque
                Q[i] = np.dot( T[i] , T[i] )
                
            else:
                
                # Bad option
                Q[i] = 9999999999 # INF
               # print 'bad option'
            
        
        # Optimal dsicrete mode
        i_star = Q.argmin()
                        
        # Hysteresis
        if self.hysteresis:
            gear_shift_gain = np.linalg.norm( T[ i_star ] - T[ self.last_gear_i ] )
            if gear_shift_gain < self.hys_level :
                # Keep old gear ratio
                i_star = self.last_gear_i
            
        u  = np.append( T[ i_star ] , self.uD( i_star ) )
        
        return u
        

    ############################
    def computed_torque( self , ddq_r , x , R ):
        """ 
        
        Given actual state and gear ratio, compute torque necessarly for a given acceleration vector
        
        """
        
        [ q , dq ] = self.R.x2q( x )   # from state vector (x) to angle and speeds (q,dq)
        
        F = self.R.T( q , dq , ddq_r , R ) # Generalized force necessarly
        
        return F
        
        
    ############################
    def uD( self , i  ):
        """ 
        
        Return the discrete value for the gear ratio
        
        1-Dof # -> input is directly the ratio
        
        else  # -> input is the index
        
        """
        
        if self.R.dof == 1 :
            
            return self.R.R[ i ]
            
        else:
            
            return i
        
        

    


        
        