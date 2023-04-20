#!/usr/bin/python

import argparse
import sys
import re
import more_itertools as mit


def parse_input(input):
    neighborhoods = {}
    owners = {}

    # Both of these regular expressions make the assumption that the attribute values go from 0 to 10 inclusive.
    # They also allow for the possibility of the homeowner/neighborhood ID or neighborhood preferences of being
    # empty captures in order to simplify the regexp structure. We'll check for those cases further down.

    # These could theoretically be combined into a single super regexp at some cost to both readability and
    # (possibly) run-time performance, but would allow a lot of simplification and DRY'ing the code that follows

    # The parsing results in a nested dict for neighborhoods and another for homeowners. The keys for each are
    # their respective IDs and the value is a dict with the fit ratings. Homeowners values also include a list of
    # neighborhood preference rankings. Neighborhoods include an (initially) empty list of owners.

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
            sys.exit("Error: malformed input line: " + line)


    # We need to make sure that homeowners have only expressed preference rankings over
    # neighborhoods included in the data set or the matching algorithm will barf.
    #
    # The set difference below is actually a little stricter than necessary because it
    # also ends up making sure that there are no neighborhoods for which there is no expressed
    # prefence by *any* homeowner.

    neighborhood_set = set(neighborhoods.keys())
    owners_neighborhood_set = set(())
    for entry in owners:
        owners_neighborhood_set.update(owners[entry]['preferences'])

    differences = owners_neighborhood_set.symmetric_difference(neighborhood_set)

    if len(differences) > 0:
        sys.exit("Error: found neighborhood preferences for non-present neighborhoods")

    return [neighborhoods, owners]


# A simple convenience method to accept two fit vectors and return
# a tuple containing the passed ID and the dot product of the vectors

def calc_fit_tuple(rating_vector1, rating_vector2, id):
    return (id, mit.dotproduct(rating_vector1, rating_vector2))


# Matching homeowners to neighborhoods solely on the fit vectors is a standard
# assignment problem for which an optimal solution could be found with LP or
# a graph traversal algorithm, but the addition of ordinal preferences converts
# it into an NP-hard problem (I think?), so we'll use a greedy algorithm instead.

def assign_owners(neighborhoods, owners):
    assignment_fits = {}
    assigned = {}
    max_owners = len(owners)/len(neighborhoods)

    # Create a new dict which, for each homeowner, contains a list of tuples with
    # their fit to each neighborhood ordered by their preference ranking. This
    # dict also ends up acting as the queue of owners awaiting assignment to neighborhoods

    for owner in owners:
        assignment_fits[owner] = [calc_fit_tuple(owners[owner]['ratings'], neighborhoods[n]['ratings'], n) for n in owners[owner]['preferences']]

    while len(assignment_fits) > 0:

        # Since we're greedy, pluck off the owner with the highest fit value for their first choice
        next_owner = max(assignment_fits, key=lambda n: assignment_fits[n][0][1])

        # Loop over the neighborhoods in order of preference
        for choice in assignment_fits[next_owner]:

            current_owners = neighborhoods[choice[0]]['owners']

            # If the current neighborhood isn't full, assign the owner to it.
            if len(current_owners) < max_owners:
                current_owners.append((next_owner, choice[1]))
                break

            # If the neighborhood is full, see if this owner has a higher fit than
            # lowest fit current owner. If so, add them to the neighborhood and move
            # the lowest fit owner back to the assignment queue
            elif choice[1] > min(current_owners, key=lambda owner: owner[1])[1]:
                current_owners.append((next_owner, choice[1]))
                current_owners.sort(key=lambda owner: owner[1], reverse=True)
                bumped = current_owners.pop()
                assignment_fits[bumped[0]] = assigned[bumped[0]]
                assigned.pop(bumped[0])
                break

        # As long as the assumption holds that owners modulo neighborhoods is zero
        # we can be sure that this owner was assigned somewhere, so move them out
        # of the assignment queue
        assigned[next_owner] = assignment_fits[next_owner]
        assignment_fits.pop(next_owner)


cmd_description = """
Match homeowners with neighborhoods based on preferences

The input data should contain information on both homeowners and neighborhoods with one record per line

The data format should be as follows:

for a Neighborhood
N N0 E:7 W:7 R:10

for a Homeowner
H H0 E:3 W:9 R:2 N2>N0>N1

The assignments of Homeowner to Neighborhood will be output as follows
N0: H5(161) H11(154) H2(128) H4(122)
"""

p = argparse.ArgumentParser(description=cmd_description, formatter_class=argparse.RawTextHelpFormatter)
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
