// adjust_pv.cpp

#include "adjust_pv.h"
#include <iostream>
#include <cmath> // For trigonometric functions

// Define the optimal azimuth angle (e.g., south-facing in the Northern Hemisphere)
const double OPTIMAL_AZIMUTH = 180.0; // Degrees

// Define the optimal tilt angle (you can adjust this based on your requirements)
const double OPTIMAL_TILT = 30.0; // Degrees

double adjust_pv_estimate(double input, double multiplier, double azimuth, double tilt) {
    // Apply multiplier
    double adjusted_value = input * multiplier;

    // Calculate azimuth factor
    double angle_difference_azimuth = std::abs(azimuth - OPTIMAL_AZIMUTH);
    // Simple model: PV efficiency decreases by 0.5% for each degree away from optimal
    double azimuth_factor = 1.0 - (0.005 * angle_difference_azimuth);
    // Ensure the azimuth factor doesn't drop below a reasonable threshold (e.g., 50%)
    if (azimuth_factor < 0.5) {
        azimuth_factor = 0.5;
    }

    // Calculate tilt factor
    double angle_difference_tilt = std::abs(tilt - OPTIMAL_TILT);
    // Simple model: PV efficiency decreases by 0.3% for each degree away from optimal
    double tilt_factor = 1.0 - (0.003 * angle_difference_tilt);
    // Ensure the tilt factor doesn't drop below a reasonable threshold (e.g., 60%)
    if (tilt_factor < 0.6) {
        tilt_factor = 0.6;
    }

    // Apply azimuth and tilt factors
    adjusted_value *= azimuth_factor * tilt_factor;

    std::cout << "Adjusting PV estimate: Input = " << input 
              << ", Multiplier = " << multiplier 
              << ", Azimuth = " << azimuth 
              << ", Azimuth Factor = " << azimuth_factor 
              << ", Tilt = " << tilt 
              << ", Tilt Factor = " << tilt_factor 
              << ", Adjusted Value = " << adjusted_value << std::endl;

    return adjusted_value;
}