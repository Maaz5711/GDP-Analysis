def filter_by_region(data, region_name):
    return [row for row in data if row['Region'] == region_name]


def filter_by_year(data, year):
    return [row for row in data if row['Year'] == year]


def get_values(data):
    return [row['Value'] for row in data]


def calculate_sum(values):
    if not values:
        return 0.0
    return sum(values)


def calculate_average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def process_data(data, config):

    region_data = filter_by_region(data, config['region'])
    target_data = filter_by_year(region_data, config['year'])

    gdp_values = get_values(target_data)

    operation = config['operation'].lower()

    if operation == "sum":
        result = calculate_sum(gdp_values)

    elif operation == "average":
        result = calculate_average(gdp_values)

    else:
        raise ValueError("Invalid operation in config.")

    return region_data, result

