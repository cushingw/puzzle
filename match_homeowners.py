#!/usr/bin/python

import argparse
import sys
import re
import more_itertools as mit


def parse_input(input):
    neighborhoods = {}
    owners = {}

    Nre = re.compile(r'^N (?P<id>.*?) E:(?P<eff>[0-9]|10) W:(?P<water>[0-9]|10) R:(?P<resil>[0-9]|10)$')
    Hre = re.compile(r'^H (?P<id>.*?) E:(?P<eff>[0-9]|10) W:(?P<water>[0-9]|10) R:(?P<resil>[0-9]|10) (?P<prefs>.*?)$')

    for line in input.readlines():
        try:
            if line[0] == 'N':
                match = Nre.match(line)
                if not match:
                    raise ValueError

                data = match.groupdict()
                if len(data['id']) == 0:
                    raise ValueError

                neighborhoods[data['id']] = {
                    'ratings': [int(data['eff']), int(data['water']), int(data['resil'])],
                    'owners': []
                }

            elif line[0] == 'H':
                match = Hre.match(line)
                if not match:
                    raise ValueError

                data = match.groupdict()
                if len(data['id']) == 0:
                    raise ValueError

                if len(data['prefs']) == 0:
                    raise ValueError

                owners[data['id']] = {
                    'ratings': [int(data['eff']), int(data['water']), int(data['resil'])],
                    'preferences': data['prefs'].split('>')
                }
        except ValueError:
            sys.exit("Error: malformed input line: ", line)

    neighborhood_set = set(neighborhoods.keys())
    owners_neighborhood_set = set(())
    for entry in owners:
        owners_neighborhood_set.update(owners[entry]['preferences'])

    differences = owners_neighborhood_set.symmetric_difference(neighborhood_set)

    if len(differences) > 0:
        sys.exit("Error: found neighborhood preferences for non-present neighborhoods")

    return [neighborhoods, owners]


def calc_fit_tuple(rating_vector1, rating_vector2, id):
    return (id, mit.dotproduct(rating_vector1, rating_vector2))


def assign_owners(neighborhoods, owners):
    assignment_fits = {}
    assigned = {}
    max_owners = len(owners)/len(neighborhoods)

    for owner in owners:
        assignment_fits[owner] = [calc_fit_tuple(owners[owner]['ratings'], neighborhoods[n]['ratings'], n) for n in owners[owner]['preferences']]

    while len(assignment_fits) > 0:
        next_owner = max(assignment_fits, key=lambda n: assignment_fits[n][0][1])

        for choice in assignment_fits[next_owner]:
            current_owners = neighborhoods[choice[0]]['owners']
            if len(current_owners) < max_owners:
                current_owners.append((next_owner, choice[1]))
                break
            elif choice[1] > min(current_owners, key=lambda owner: owner[1])[1]:
                current_owners.append((next_owner, choice[1]))
                current_owners.sort(key=lambda owner: owner[1], reverse=True)
                bumped = current_owners.pop()
                assignment_fits[bumped[0]] = assigned[bumped[0]]
                assigned.pop(bumped[0])
                break

        assigned[next_owner] = assignment_fits[next_owner]
        assignment_fits.pop(next_owner)




# neighborhoods = {
#     'N0': {
#         'ratings': [7, 7, 10],
#         'owners': []
#     },
#     'N1': {
#         'ratings': [2, 1, 1],
#         'owners': []
#     },
#     'N2': {
#         'ratings': [7, 6, 4],
#         'owners': []
#     }
# }

# owners = {
#     'H0': {
#         'ratings': [3,9,2],
#         'preferences': ['N2','N0','N1'],
#         'neighborhood': None
#     },
#     'H1': {
#         'ratings': [4,3,7],
#         'preferences': ['N0','N2','N1'],
#         'neighborhood': None
#     },
#     'H2': {
#         'ratings': [4,0,10],
#         'preferences': ['N0','N2','N1'],
#         'neighborhood': None
#     },
#     'H3': {
#         'ratings': [10,3,8],
#         'preferences': ['N2','N0','N1'],
#         'neighborhood': None
#     },
#     'H4': {
#         'ratings': [6,10,1],
#         'preferences': ['N0','N2','N1'],
#         'neighborhood': None
#     },
#     'H5': {
#         'ratings': [6,7,7],
#         'preferences': ['N0','N2','N1'],
#         'neighborhood': None
#     },
#     'H6': {
#         'ratings': [8,6,9],
#         'preferences': ['N2','N1','N0'],
#         'neighborhood': None
#     },
#     'H7': {
#         'ratings': [7,1,5],
#         'preferences': ['N2','N1','N0'],
#         'neighborhood': None
#     },
#     'H8': {
#         'ratings': [8,2,3],
#         'preferences': ['N1','N0','N2'],
#         'neighborhood': None
#     },
#     'H9': {
#         'ratings': [10,2,1],
#         'preferences': ['N1','N2','N0'],
#         'neighborhood': None
#     },
#     'H10': {
#         'ratings': [6,4,5],
#         'preferences': ['N0','N2','N1'],
#         'neighborhood': None
#     },
#     'H11': {
#         'ratings': [8,4,7],
#         'preferences': ['N0','N1','N2'],
#         'neighborhood': None
#     },
# }

p = argparse.ArgumentParser(description='Match homeowners with neighborhoods based on preferences')
p.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
               help='Input file (default: standard input)')
p.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
               help='Output file (default: standard output)')

args = p.parse_args()

neighborhoods, owners = parse_input(args.input)
assign_owners(neighborhoods, owners)
for n in neighborhoods:
    owner_list = ' '.join([f"{own[0]}({own[1]})" for own in neighborhoods[n]['owners']])
    print(f"{n}: {owner_list}", file=args.output)
