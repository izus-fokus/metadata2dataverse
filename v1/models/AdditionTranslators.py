from datetime import date

class DateAdder(object):
    ''' returns Date of service '''
    def main(self,source_key):
        today = date.today()
        date_formatted = today.strftime("%Y-%m-%d")
        return [date_formatted]
    
class ContributorRole(object):
    ''' returns '''
    def main(self,source_key):
        if source_key == "sponsor" or source_key == "funder":
            return "Funder"
        if source_key == "editor":
            return "Editor"
        if source_key == "copyrightHolder":
            return "Rightsholder"