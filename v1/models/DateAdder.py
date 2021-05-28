from datetime import date

class DateAdder(object):
    ''' returns Date of service '''
    def main(self):
        today = date.today()
        date_formatted = today.strftime("%Y-%m-%d")
        return date_formatted