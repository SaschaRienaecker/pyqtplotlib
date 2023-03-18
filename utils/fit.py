import numpy as np
from scipy.optimize import curve_fit


def fit_curve(x_data, y_data, curve_type):
    if curve_type == 'gaussian':
        # Define a Gaussian function
        def gaussian(x, a, x0, sigma):
            return a*np.exp(-(x-x0)**2/(2*sigma**2))

        # Initial guess for the Gaussian fit parameters
        p0 = [np.max(y_data), np.mean(x_data), np.std(x_data)]

        # Fit the data to the Gaussian function
        popt, _ = curve_fit(gaussian, x_data, y_data, p0=p0)

        # Return the fitted Gaussian function and parameters
        return gaussian, popt

    elif curve_type == 'lorentzian':
        # Define a Lorentzian function
        def lorentzian(x, a, x0, gamma):
            return a*gamma**2/((x-x0)**2+gamma**2)

        # Initial guess for the Lorentzian fit parameters
        p0 = [np.max(y_data), np.mean(x_data), np.std(x_data)]

        # Fit the data to the Lorentzian function
        popt, _ = curve_fit(lorentzian, x_data, y_data, p0=p0)

        # Return the fitted Lorentzian function and parameters
        return lorentzian, popt

    else:
        # Invalid curve type
        raise ValueError('Invalid curve type')
