#!/usr/bin/env python3

# (C) Alexander Korsunsky, 2016

import krpc
import time
import sys
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("outfile", help="Output filename")
parser.add_argument("-i", "--interval", help="Interval", type=float, default=1.0)
args = parser.parse_args()


# Get connection
try:
    print("Connecting to KSP. Please accept the connection from kRPC window in KSP")
    conn = krpc.connect(name="Python flight data logger")
    
except krpc.error.NetworkError as e:
    print("Failed to connect to kRPC server. Is KSP and the kRPC Server running?")
    exit(1)

vessel = conn.space_center.active_vessel
flight = conn.space_center.active_vessel.flight(conn.space_center.active_vessel.orbit.body.reference_frame)
orbit = conn.space_center.active_vessel.orbit

# function to regenerate parts list
def parts_list():
    parts_list.max_skin_temp = [p.max_skin_temperature for p in vessel.parts.all]
    parts_list.name = [p.name for p in vessel.parts.all]
    return (parts_list.max_skin_temp, parts_list.name)

parts_list();

outfilename = args.outfile
interval = args.interval

print("Starting log. Please stop it by pressing Control-C")
try:
    with open(outfilename, 'wt') as outfile:
        outfile.write("ut,"
            "mean_altitude,"
            "surf_speed,"
            "g_force,"
            "aoa,"
            "sideslip,"
            "atmosphere_density,"
            "dynamic_pressure,"
            "aerodynamic_force,"
            "highest_skin_temp,"
            "highest_skin_temp_part,"
            "critical_skin_temp,"
            "critical_skin_temp_part,"
            "ablator"
            "\n")
        
        while True:
            # refresh parts list if partcount has changed
            partcount = len(vessel.parts.all)
            if partcount < 1:
                print("\nIt seems, there are no more parts on this vessel. I'm sorry for your loss.")
                exit(0)
                break
            if partcount != len(parts_list.name):
                parts_list()
    
            skin_temps = [p.skin_temperature for p in vessel.parts.all]
            hightest_skin_temp_ind = np.argmax(skin_temps)
            critical_skin_temp_ind = np.argmax([t/m for t,m in zip(skin_temps,parts_list.max_skin_temp)])
    
            line = ("{ut},"
            "{mean_altitude},"
            "{surf_speed},"
            "{g_force},"
            "{aoa},"
            "{sideslip},"
            "{atmosphere_density},"
            "{dynamic_pressure},"
            "{aerodynamic_force},"
            "{highest_skin_temp},"
            "\"{highest_skin_temp_part}\","
            "{critical_skin_temp},"
            "\"{critical_skin_temp_part}\","
            "{ablator}"
            "\n").format(
                ut=conn.space_center.ut,
                surf_speed=flight.speed,
                mean_altitude=flight.mean_altitude,
                g_force=flight.g_force,
                aoa=flight.angle_of_attack,
                sideslip=flight.sideslip_angle,
                #sideslip=flight.sideslip_angle,,
                atmosphere_density=flight.atmosphere_density,
                dynamic_pressure=flight.dynamic_pressure,
                aerodynamic_force=np.linalg.norm(flight.drag),
                highest_skin_temp=skin_temps[hightest_skin_temp_ind],
                highest_skin_temp_part=parts_list.name[hightest_skin_temp_ind],
                critical_skin_temp=skin_temps[critical_skin_temp_ind],
                critical_skin_temp_part=parts_list.name[critical_skin_temp_ind],
                ablator=vessel.resources.amount('Ablator')
            )

            # write line
            outfile.write(line)
            
            # write marker
            print('.', end="")
            sys.stdout.flush()

    
            time.sleep(interval)
except KeyboardInterrupt as e:
    print("\nThanks for logging. Bye!")