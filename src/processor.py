# filter by specific region
def filter_by_region(data, region_name):
    return [row for row in data if row['Region'] == region_name]

# filter via year
def filter_by_year(data, year):
    return [row for row in data if row['Year'] == year]

# get GDP values from filtered data
def get_values(data):
    return [row['Value'] for row in data]

#sum & average  of GDP values

def calculate_sum(values):
    if not values:
        return 0.0
    return sum(values)


def calculate_average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


# main fuction to process data as per config
def process_data(data, config):

    region_data = filter_by_region(data, config['region'])
    target_data = filter_by_year(region_data, config['year'])
    gdp_values = get_values(target_data)

    # operation to perform?
    operation = config['operation'].lower()

    if operation == "sum":
        result = calculate_sum(gdp_values)
    elif operation == "average":
        result = calculate_average(gdp_values)
    else:
        raise ValueError("Invalid operation selected!")

    return region_data, result
