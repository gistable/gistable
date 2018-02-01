#!/usr/bin/env python3

# Copyright [1999-2015] Wellcome Trust Sanger Institute and the EMBL-European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests, sys, argparse

parser = argparse.ArgumentParser(description='Emit chromosome sizes from Ensembl REST servers')
parser.add_argument('species', metavar='S', type=str, help='The species to retrieve', default='human', nargs='?')
parser.add_argument('--ensembl_genomes', '-eg', dest='eg', action='store_true', help='Use the Ensembl Genomes REST server', default=False)
parser.add_argument('--just_chroms', '-chr', dest='chr', action='store_true', help='Filter output for just those regions with coord_system tagged as chromsomes', default=False)
args = parser.parse_args()

if args.eg:
    server = "http://rest.ensemblgenomes.org"
else:
    server = "http://rest.ensembl.org"

ext = "/info/assembly/"

r = requests.get(server+ext+args.species, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
    print("Species "+args.species+" might not exist on this server")
    r.raise_for_status()
    sys.exit()
 
decoded = r.json()
regions = decoded["top_level_region"]
regions.sort(key=lambda r: r["name"])

for r in regions:
    if args.chr and r["coord_system"] != 'chromosome':
        continue
    print("{}\t{}".format(r["name"], r["length"]))
