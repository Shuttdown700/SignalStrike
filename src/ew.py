def convert_watts_to_dBm(p_watts: float) -> float:
    """
    Converts watts to dBm.

    Parameters
    ----------
    p_watts : float
        Power in watts (W).

    Returns
    -------
    float
        Power in dBm.

    """
    import math
    # input assertation
    assert isinstance(p_watts,(float,int)) and p_watts >= 0, 'Wattage needs to be a float greater than zero.'
    # return power in dBm
    return 10*math.log10(1000*p_watts)

def theoretical_emission_distance(P_t_watts : float,
                      f_MHz : float,
                      G_t : float,
                      G_r : float,
                      R_s : float,
                      path_loss_coeff=3) -> float:
    """
    Returns theoretical maximum distance of emission.

    Parameters
    ----------
    P_t_watts : float
        Power output of transmitter in watts (W).
    f_MHz : float
        Operating frequency in MHz.
    G_t : float
        Transmitter antenna gain in dBi.
    G_r : float
        Receiver antenna gain in dBi.
    R_s : float
        Receiver sensitivity in dBm *OR* power received in dBm.
    path_loss_coeff : float, optional
        Coefficient that considers partial obstructions such as foliage. 
        The default is 3.

    Returns
    -------
    float
        Theoretical maximum distance in km.

    """
    import math
    # return 10**((convert_watts_to_dBm(P_t_watts)+(G_t)-32.4-(20*math.log10(f_MHz))+(G_r)-R_s)/(20))
    return 10**((convert_watts_to_dBm(P_t_watts)+(G_t)-32.4-(10*path_loss_coeff*math.log10(f_MHz))+(G_r)-R_s)/(10*path_loss_coeff))

def emission_optical_maximum_distance(t_h : float, r_h : float) -> float:
    """
    Returns theoretical maximum line-of-sight between transceivers.

    Parameters
    ----------
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).

    Returns
    -------
    float
        Maximum line-of-sight due to Earth curvature in km.

    """
    import math
    return (math.sqrt(2*6371000*r_h+r_h**2)/1000)+(math.sqrt(2*6371000*t_h+t_h**2)/1000)

def emission_optical_maximum_distance_with_ducting(t_h : float,
                                                   r_h : float,
                                                   f_MHz : float,
                                                   temp_f : float,
                                                   weather_coeff=4/3) -> float:
    """
    Returns theoretical maximum line-of-sight between transceivers with ducting consideration.

    Parameters
    ----------
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).
    f_MHz : float
        Operating frequency in MHz.
    temp_f : float
        ENV Temperature in fahrenheit.
    weather_coeff : float, optional
        ENV Weather conditions coefficient. The default is 4/3.

    Returns
    -------
    float
        Maximum line-of-sight due to Earth curvature and ducting in km.

    """
    import math
    return (math.sqrt(2*weather_coeff*6371000*r_h+temp_f**2)/1000)+(math.sqrt(2*weather_coeff*6371000*t_h+f_MHz**2)/1000)

def get_emission_distance(P_t_watts : float,
                          f_MHz : float,
                          G_t : float,
                          G_r : float,
                          R_s : float,
                          t_h : float,
                          r_h : float,
                          temp_f : float,
                          path_loss_coeff=3,
                          weather_coeff=4/3,
                          pure_pathLoss=False) -> float:
    """
    Returns theoretical maximum line-of-sight between transceivers all pragmatic consideration.

    Parameters
    ----------
    P_t_watts : float
        Power output of transmitter in watts (W).
    f_MHz : float
        Operating frequency in MHz.
    G_t : float
        Transmitter antenna gain in dBi.
    G_r : float
        Receiver antenna gain in dBi.
    R_s : float
        Receiver sensitivity in dBm *OR* power received in dBm.
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).
    temp_f : float
        ENV Temperature in fahrenheit.
    weather_coeff : float, optional
        ENV Weather conditions coefficient. The default is 4/3.

    Returns
    -------
    float
        Maximum line-of-sight due to path-loss, Earth curvature and ducting in km.

    """
    path_loss_coeff = float(path_loss_coeff)
    path_loss = theoretical_emission_distance(P_t_watts,f_MHz,G_t,G_r,R_s,path_loss_coeff)
    # earth_curve = emission_optical_maximum_distance(t_h,r_h)
    earth_curve_with_ducting = emission_optical_maximum_distance_with_ducting(t_h,r_h,f_MHz,temp_f,weather_coeff)
    emissions_distances = [path_loss,earth_curve_with_ducting]
    if pure_pathLoss:
        return path_loss
    else:
        return min(emissions_distances)
