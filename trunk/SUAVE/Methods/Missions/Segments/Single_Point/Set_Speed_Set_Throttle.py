## @ingroup Methods-Missions-Segments-Single_Point
# Set_Speed_Set_Throttle.py
# 
# Created:  Mar 2017, T. MacDonald
# Modified: Jul 2017, T. MacDonald
#           Aug 2017, E. Botero

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

autograd.numpy import np

# ----------------------------------------------------------------------
#  Initialize Conditions
# ----------------------------------------------------------------------

## @ingroup Methods-Missions-Segments-Single_Point
def initialize_conditions(segment,state):
    """Sets the specified conditions which are given for the segment type.

    Assumptions:
    A fixed speed and throttle

    Source:
    N/A

    Inputs:
    segment.altitude                               [meters]
    segment.air_speed                              [meters/second]
    segment.throttle                               [unitless]
    segment.z_accel                                [meters/second^2]
    state.unknowns.x_accel                         [meters/second^2]

    Outputs:
    conditions.frames.inertial.acceleration_vector [meters/second^2]
    conditions.frames.inertial.velocity_vector     [meters/second]
    conditions.frames.inertial.position_vector     [meters]
    conditions.freestream.altitude                 [meters]
    conditions.frames.inertial.time                [seconds]

    Properties Used:
    N/A
    """      
    
    # unpack
    alt        = segment.altitude
    air_speed  = segment.air_speed
    throttle   = segment.throttle
    z_accel    = segment.z_accel
    x_accel    = state.unknowns.x_accel
    conditions = state.conditions 
    
    # check for initial altitude
    if alt is None:
        if not state.initials: raise AttributeError('altitude not set')
        alt = -1.0 * state.initials.conditions.frames.inertial.position_vector[-1,2]
        segment.altitude = alt
    
    # pack
    state.conditions.freestream.altitude[:,0]             = alt
    state.conditions.frames.inertial.position_vector[:,2] = -alt # z points down
    state.conditions.frames.inertial.velocity_vector[:,0] = air_speed
    state.conditions.propulsion.throttle[:,0]             = throttle
    state.conditions.frames.inertial.acceleration_vector = np.array([[x_accel,0.0,z_accel]])

## @ingroup Methods-Missions-Segments-Single_Point    
def update_weights(segment,state):
    """Sets the gravity force vector during the segment

    Assumptions:
    A fixed speed and altitde

    Source:
    N/A

    Inputs:
    conditions:
        weights.total_mass                          [kilogram]
        freestream.gravity                          [meters/second^2]

    Outputs:
    conditions.frames.inertial.gravity_force_vector [newtons]


    Properties Used:
    N/A
    """         
    
    # unpack
    conditions = state.conditions
    m0         = conditions.weights.total_mass[0,0]
    g          = conditions.freestream.gravity

    # weight
    W = m0*g

    # pack
    conditions.frames.inertial.gravity_force_vector[:,2] = W

    return

## @ingroup Methods-Missions-Segments-Single_Point
def unpack_unknowns(segment,state):
    """ Unpacks the x accleration and body angle from the solver to the mission
    
        Assumptions:
        N/A
        
        Inputs:
            state.unknowns:
                x_accel                             [meters/second^2]
                body_angle                          [radians]
            
        Outputs:
            state.conditions:
                frames.inertial.acceleration_vector [meters/second^2]
                frames.body.inertial_rotations      [radians]

        Properties Used:
        N/A
                                
    """      
    
    # unpack unknowns
    x_accel    = state.unknowns.x_accel
    body_angle = state.unknowns.body_angle
    
    # apply unknowns
    state.conditions.frames.inertial.acceleration_vector[0,0] = x_accel # Update for AD
    state.conditions.frames.body.inertial_rotations[:,1]      = body_angle[:,0]     # Update for AD 