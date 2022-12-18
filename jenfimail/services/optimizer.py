from django.db import transaction
from django.db.models import Sum

from pulp import LpMinimize, LpMaximize, LpProblem, LpStatus, lpSum, LpVariable
import numpy as np

class OptimizerService():
    LOWER_BOUND = 0
    SENSE = LpMinimize
    CAT_BINARY = 'Binary'

    def __init__(self, **args):
        self.problem_name = args.get('name', 'mail-scheduler')
        self.shift_duration_hrs = args.get('shift_duration', 3)
        self.shifts_per_day = 24 / self.shift_duration_hrs
        self.profit_margin_percentage = float(args.get('profit_margin_percentage', 0))

    def minimize_cost(self, lines, trains, parcels):
        lines = [line.id for line in lines]
        trains = list(trains)
        parcel_volume = parcels.aggregate(Sum('volume')) #sum([parcel.volume for parcel in parcels])
        parcel_weight = parcels.aggregate(Sum('weight')) #sum([parcel.weight for parcel in parcels])

        model = LpProblem(name=self.problem_name, sense=self.SENSE)

        # decision variables
        no_of_variables = len(lines) * len(trains)
        x = { i: LpVariable(name=f'x{i}', lowBound=self.LOWER_BOUND, cat=self.CAT_BINARY) for i in range(no_of_variables) }

        # base matrix with the train X line constraint implemented
        assignment_matrix = np.zeros((len(lines), len(trains)))
        for (i, j), _ in np.ndenumerate(assignment_matrix):
            assignment_matrix[i][j] = 1 if lines[i] in [line.id for line in trains[j].lines.all()] else 0
        assignment_vector = assignment_matrix.flatten()

        # objective function
        model += lpSum(trains[i % len(trains)].cost * assignment_vector[i] * x[i] for i in range(no_of_variables)), 'cost'

        # constraints
        model += (lpSum(trains[i % len(trains)].weight_capacity * assignment_vector[i] * x[i] for i in range(no_of_variables)) >= parcel_weight), 'parcel weight'
        model += (lpSum(trains[i % len(trains)].volume_capacity * assignment_vector[i] * x[i] for i in range(no_of_variables)) >= parcel_volume), 'parcel volume'

        for t in range(len(trains)):
            model += (lpSum(assignment_vector[t + len(trains) * i] * x[t + len(trains) * i] for i in range(len(lines))) <= 1), 'train one-time' + str(trains[t].id)

        print(model)
        status = model.solve()

        # infeasible
        if status == -1:
            return None, None

        # map schedule
        i = 0
        schedule = []
        for var in x.values():
            if var.value() == 1:
                schedule.append((
                    trains[i % len(trains)],
                    lines[int(i/len(lines))]
                ))
            i += 1

        return model.objective.value(), schedule

    @transaction.atomic
    def set_optimal_cost(self, shipment):
        cost_per_weight = shipment.train.cost / shipment.weight
        for parcel in shipment.parcels.all():
            parcel.cost = round(parcel.weight * cost_per_weight * (1 + self.profit_margin_percentage), 2)
            parcel.save()
