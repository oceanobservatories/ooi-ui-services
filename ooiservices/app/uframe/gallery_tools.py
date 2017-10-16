#!/usr/bin/env python

"""
Support for gallery interface, functions utilized for processing information.
"""
__author__ = 'Edna Donoughe'


from flask import current_app

def _get_date_bound(data, bound='first'):
    """
    Get 'first' or 'last' date in data dictionary.
    """
    year = None
    month = None
    day = None
    try:
        # Verify data is not null or empty, exception handling
        if not data or data is None:
            message = 'Data to be evaluated for first date is null or empty.'
            raise Exception(message)
        # Verify data is dictionary.
        if not isinstance(data, dict):
            message = 'Data provided for first data is not a dictionary.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - -
        # Get dictionary keys (years).
        #- - - - - - - - - - - - - - - - - - -
        str_year_keys = data.keys()
        int_year_keys = []
        for item in str_year_keys:
            try:
                int_key = int(item)
            except:
                continue

            if int_key not in int_year_keys:
                int_year_keys.append(int_key)
            else:
                continue

        if int_year_keys:
            if bound == 'first':
                int_year_keys.sort()
            else:
                int_year_keys.sort(reverse=True)
            year = int_year_keys[0]

        if year is None:
            message = 'Unable to successfully process year for first data in data.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - -
        # Get dictionary keys (months).
        #- - - - - - - - - - - - - - - - - - -
        str_month_keys = data[str(year)].keys()
        int_month_keys = []
        for item in str_month_keys:
            try:
                int_key = int(item)
            except:
                continue
            if int_key not in int_month_keys:
                int_month_keys.append(int_key)
            else:
                continue
        if int_month_keys:
            if bound == 'first':
                int_month_keys.sort()
            else:
                int_month_keys.sort(reverse=True)
            month = int_month_keys[0]

        if month is None:
            message = 'Unable to successfully process month for first data in data.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - -
        # Get dictionary keys (days).
        #- - - - - - - - - - - - - - - - - - -
        if month <= 9:
            str_month = '0' + str(month)
        else:
            str_month = str(month)
        str_day_keys = data[str(year)][str_month]   #.keys()
        int_day_keys = []
        for item in str_day_keys:
            try:
                int_key = int(item)
            except:
                continue

            if int_key not in int_day_keys:
                int_day_keys.append(int_key)
            else:
                continue

        if int_day_keys:
            if bound == 'first':
                int_day_keys.sort()
            else:
                int_day_keys.sort(reverse=True)
            day = int_day_keys[0]

        if day is None:
            message = 'Unable to successfully process day for first data in data.'
            raise Exception(message)

        # Prepare formatted output
        str_year = str(year)
        if month <= 9:
            str_month = '0' + str(month)
        else:
            str_month = str(month)
        if day <= 9:
            str_day = '0' + str(day)
        else:
            str_day = str(day)
        result = '-'.join([str_year, str_month, str_day])
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def verify_date(data, date, type=None):
    """
    Verify data has content and date is valid and present in data.
    Optional 'type' permits improved error processing.
    """
    try:
        if not data or data is None:
            message = 'No data provided to process for range processing.'
            raise Exception(message)
        if '-' not in date:
            message = 'Malformed start date provided (%r) for range of data.' % date
            raise Exception(message)

        year, month, day = date.split('-', 3)
        if year not in data:
            if type and type is not None:
                message = '%s year field is invalid for data provided.' % type.title()
            else:
                message = 'Year is invalid for data provided.'
            raise Exception(message)
        if month not in data[year]:
            if type and type is not None:
                message = '%s month field is invalid for data provided.' % type.title()
            else:
                message = 'Month is invalid for data provided.'
            raise Exception(message)
        if day not in data[year][month]:
            if type and type is not None:
                message = '%s day field is invalid for data provided.' % type.title()
            else:
                message = 'Day is invalid for data provided.'
            raise Exception(message)

        return True
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_range_data(data, first_range_date, last_range_date):
    """
    Get slice of data for range first_date to last_date inclusive.
    """
    try:
        try:
            verify_date(data, first_range_date, 'first')
            verify_date(data, last_range_date, 'last')
        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            raise Exception(message)

        # Get range parameters for checking data in bounds.
        first_range_year, first_range_month, first_range_day = first_range_date.split('-', 3)
        last_range_year, last_range_month, last_range_day = last_range_date.split('-', 3)

        # Get integer values of parameters.
        int_first_range_year = int(first_range_year)
        int_first_range_month = int(first_range_month)
        int_first_range_day = int(first_range_day)
        int_last_range_year = int(last_range_year)
        int_last_range_month = int(last_range_month)
        int_last_range_day = int(last_range_day)

        str_year_keys = data.keys()
        int_year_keys = []
        for item in str_year_keys:
            try:
                int_key = int(item)
            except:
                continue

            if int_key not in int_year_keys:
                int_year_keys.append(int_key)
            else:
                continue

        if int_year_keys:
            int_year_keys.sort()

        # Trim data to years.
        if int_first_range_year not in int_year_keys:
            message = 'The start date provided for range is not within the available data.'
            raise Exception(message)
        if int_last_range_year not in int_year_keys:
            message = 'The end date provided for range is not within the available data.'
            raise Exception(message)

        year_result = {}
        years_equal  = False
        months_equal = False
        days_equal = False
        if int_first_range_year == int_last_range_year:
            year_result[str(int_first_range_year)] = data[str(int_first_range_year)]
            years_equal = True
        else:
            for year in int_year_keys:
                if year >= int_first_range_year and year <= int_last_range_year:
                    year_result[str(year)] = data[str(year)]
                else:
                    continue

        if int_first_range_month == int_last_range_month:
            months_equal = True
        if int_first_range_day == int_last_range_day:
            days_equal = True

        # Updated list of years in data, now filter on months in data.
        str_year_keys = year_result.keys()
        int_year_keys = []
        for item in str_year_keys:
            try:
                int_key = int(item)
            except:
                continue
            if int_key not in int_year_keys:
                int_year_keys.append(int_key)
            else:
                continue
        if int_year_keys:
            int_year_keys.sort()
        months_result = {}
        for year_inx, y in year_result.iteritems():

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # First and last year are the same
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if years_equal:
                if months_equal:
                    if days_equal:
                        months_result[first_range_year] = {}
                        months_result[first_range_year][first_range_month] = {}
                        months_result[first_range_year][first_range_month][first_range_day] = []
                        months_result[first_range_year][first_range_month][first_range_day] = \
                            year_result[first_range_year][first_range_month][first_range_day]
                        break
                    else:
                        if int_first_range_month <= 9:
                            str_month = '0' + str(int_first_range_month)
                        else:
                            str_month = str(int_first_range_month)

                        # Process all days, add if in bounds
                        str_day_keys = year_result[first_range_year][str_month].keys()
                        int_day_keys = []
                        for item in str_day_keys:
                            try:
                                int_key = int(item)
                            except:
                                continue
                            if int_key not in int_day_keys:
                                int_day_keys.append(int_key)
                            else:
                                continue
                        if int_day_keys:
                            int_day_keys.sort()

                        months_result[first_range_year] = {}
                        months_result[first_range_year][first_range_month] = {}
                        for int_day in int_day_keys:
                            if (int_day >= int_first_range_day) and (int_day <= int_last_range_day):
                                if int_day <= 9:
                                    str_day = '0' + str(int_day)
                                else:
                                    str_day = str(int_day)
                                months_result[first_range_year][str_month][str_day] = \
                                    year_result[first_range_year][str_month][str_day]
                            else:
                                continue
                else:
                    # ========================================
                    str_month_keys = year_result[first_range_year].keys()
                    int_month_keys = []
                    for item in str_month_keys:
                        try:
                            int_key = int(item)
                        except:
                            continue
                        if int_key not in int_month_keys:
                            int_month_keys.append(int_key)
                        else:
                            continue
                    if int_month_keys:
                        int_month_keys.sort()
                    months_result[first_range_year] = {}

                    # Process months...
                    for int_month in int_month_keys:
                        if (int_month >= int_first_range_month) and (int_month <= int_last_range_month):
                            if int_month <= 9:
                                str_month = '0' + str(int_month)
                            else:
                                str_month = str(int_month)
                            if str_month not in months_result[first_range_year]:
                                months_result[first_range_year][str_month] = {}
                            # Process all days in month, add if in bounds
                            # Get day keys for month...
                            str_day_keys = year_result[first_range_year][str_month].keys()

                            # get integer version of keys for month...
                            int_day_keys = []
                            for item in str_day_keys:
                                try:
                                    int_key = int(item)
                                except:
                                    continue
                                if int_key not in int_day_keys:
                                    int_day_keys.append(int_key)
                                else:
                                    continue
                            if int_day_keys:
                                int_day_keys.sort()

                            # Process days in month
                            for int_day in int_day_keys:
                                if int_month == int_first_range_month:
                                    if int_day >= int_first_range_day:
                                        if int_day <= 9:
                                            str_day = '0' + str(int_day)
                                        else:
                                            str_day = str(int_day)
                                        if str_day not in months_result[first_range_year][str_month]:
                                            months_result[first_range_year][str_month][str_day] = []
                                        months_result[first_range_year][str_month][str_day] = \
                                                    year_result[first_range_year][str_month][str_day]
                                    else:
                                        continue
                                elif int_month == int_last_range_month:
                                    if int_day <= int_last_range_day:
                                        if int_day <= 9:
                                            str_day = '0' + str(int_day)
                                        else:
                                            str_day = str(int_day)
                                        if str_day not in months_result[first_range_year][str_month]:
                                            months_result[first_range_year][str_month][str_day] = []
                                        months_result[first_range_year][str_month][str_day] = \
                                                year_result[first_range_year][str_month][str_day]
                                    else:
                                        continue
                                elif (int_month > int_first_range_month) and (int_month < int_last_range_month):
                                    if (int_day >= int_first_range_day) and (int_day <= int_last_range_day):
                                        if int_day <= 9:
                                            str_day = '0' + str(int_day)
                                        else:
                                            str_day = str(int_day)
                                        if str_day not in months_result[first_range_year][str_month]:
                                            months_result[first_range_year][str_month][str_day] = []
                                        months_result[first_range_year][str_month][str_day] = \
                                                year_result[first_range_year][str_month][str_day]
                                    else:
                                        continue

                    # ========================================

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # First and last year are NOT the same. (Different start year and end year.)
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            else:
                int_year_inx = int(year_inx)

                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                # Last year in range
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                if int_year_inx == int_last_range_year:
                    str_months_in_year = year_result[year_inx].keys()
                    for month in str_months_in_year:
                        int_month = int(month)
                        if int_month < int_last_range_month:
                            if int_month <= 9:
                                str_month = '0' + str(int_month)
                            else:
                                str_month = str(int_month)
                            if year_inx not in months_result:
                                months_result[year_inx] = {}
                            if str_month not in months_result[year_inx]:
                                months_result[year_inx][str_month] = {}
                            months_result[year_inx][str_month] = year_result[year_inx][month]
                        elif int_month == int_last_range_month:
                            if int_month <= 9:
                                str_month = '0' + str(int_month)
                            else:
                                str_month = str(int_month)
                            if year_inx not in months_result:
                                months_result[year_inx] = {}
                            if str_month not in months_result[year_inx]:
                                months_result[year_inx][str_month] = {}

                            # Get days in month, check day is greater than first_range_day.
                            str_day_keys = year_result[year_inx][month].keys()
                            int_day_keys = []
                            for item in str_day_keys:
                                try:
                                    int_key = int(item)
                                except:
                                    continue
                                if int_key not in int_day_keys:
                                    int_day_keys.append(int_key)
                                else:
                                    continue
                            if int_day_keys:
                                int_day_keys.sort()
                            for int_day in int_day_keys:
                                if int_day <= int_last_range_day:
                                    if int_day <= 9:
                                        str_day = '0' + str(int_day)
                                    else:
                                        str_day = str(int_day)
                                    months_result[year_inx][str_month][str_day] = year_result[year_inx][month][str_day]
                                else:
                                    continue

                        else:
                            continue

                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                # First year in range
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                elif int_year_inx == int_first_range_year:
                    str_months_in_year = year_result[year_inx].keys()
                    for month in str_months_in_year:
                        int_month = int(month)
                        if int_month <= 9:
                            str_month = '0' + str(int_month)
                        else:
                            str_month = str(int_month)

                        # - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Month is same as first month in range
                        # - - - - - - - - - - - - - - - - - - - - - - - - -
                        if int_month == int_first_range_month:
                            if year_inx not in months_result:
                                months_result[year_inx] = {}
                            if str_month not in months_result[year_inx]:
                                months_result[year_inx][str_month] = {}

                            # Get days in month, check day is greater than first_range_day.
                            str_day_keys = year_result[year_inx][month].keys()
                            int_day_keys = []
                            for item in str_day_keys:
                                try:
                                    int_key = int(item)
                                except:
                                    continue
                                if int_key not in int_day_keys:
                                    int_day_keys.append(int_key)
                                else:
                                    continue
                            if int_day_keys:
                                int_day_keys.sort()
                            for int_day in int_day_keys:
                                if int_day >= int_first_range_day:
                                    if int_day <= 9:
                                        str_day = '0' + str(int_day)
                                    else:
                                        str_day = str(int_day)
                                    months_result[year_inx][str_month][str_day] = year_result[year_inx][str_month][str_day]
                                else:
                                    continue

                        # - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Month is after first month in range
                        # - - - - - - - - - - - - - - - - - - - - - - - - -
                        elif int_month > int_first_range_month:
                            if year_inx not in months_result:
                                months_result[year_inx] = {}
                            if str_month not in months_result[year_inx]:
                                months_result[year_inx][str_month] = {}
                            months_result[year_inx][str_month] = year_result[year_inx][str_month]
                        else:
                            continue
                        #=======================================

                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                # In between year in range
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                elif (int_year_inx > int_first_range_year) and (int_year_inx < int_last_range_year):
                    if year_inx not in months_result:
                        months_result[year_inx] = {}
                    months_result[year_inx] = year_result[year_inx]
                else:
                    continue

        return months_result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Streamline this routine, see notes.
def _get_data_day(data, data_date):
    """
    Get data for a specific day.
    Verify year, month and day are present, get and set for return value.
    """
    try:
        if not data or data is None:
            message = 'No data provided to process for %s.' % data_date
            raise Exception(message)
        if '-' not in data_date:
            message = 'Malformed start date provided (%r) for range of data.' % data_date
            raise Exception(message)

        # Get range parameters for checking data in bounds.
        year, month, day = data_date.split('-', 2)

        # Get integer values of parameters.
        int_data_year = int(year)
        int_data_month = int(month)
        int_data_day = int(day)
        year_result = {}
        year_result[year] = data[year]
        months_result = {}
        found_it = False
        for year_inx, y in year_result.iteritems():
            int_year_inx = int(year_inx)
            #- - - - - - - - - - - - - - - - - - - - - - - - - -
            # Year
            #- - - - - - - - - - - - - - - - - - - - - - - - - -
            if int_year_inx == int_data_year:
                str_months_in_year = year_result[year_inx].keys()
                for month in str_months_in_year:
                    if found_it:
                        break
                    int_month = int(month)
                    #- - - - - - - - - - - - - - - - - - - - - - - - - -
                    # Month
                    #- - - - - - - - - - - - - - - - - - - - - - - - - -
                    if int_month == int_data_month:
                        if int_month <= 9:
                            str_month = '0' + str(int_month)
                        else:
                            str_month = str(int_month)
                        if year_inx not in months_result:
                            months_result[year_inx] = {}
                        if str_month not in months_result[year_inx]:
                            months_result[year_inx][str_month] = {}

                        #- - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Day
                        #- - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Get days in month, check day is greater than first_range_day.
                        str_day_keys = year_result[year_inx][str_month].keys()
                        int_day_keys = []
                        for item in str_day_keys:
                            try:
                                int_key = int(item)
                            except:
                                continue
                            if int_key not in int_day_keys:
                                int_day_keys.append(int_key)
                            else:
                                continue
                        if int_day_keys:
                            int_day_keys.sort()
                        for int_day in int_day_keys:
                            if int_day == int_data_day:
                                found_it = True
                                if int_day <= 9:
                                    str_day = '0' + str(int_day)
                                else:
                                    str_day = str(int_day)
                                months_result[year_inx][str_month][str_day] = year_result[year_inx][str_month][str_day]
                            else:
                                continue
                    else:
                        continue

            else:
                continue

        return months_result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)
