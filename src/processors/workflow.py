    def getPatientHTML(self, type_of_query, query):
        url = f"{self.base_url}/demographic/demographiccontrol.jsp"
        payload = {
            "search_mode": type_of_query,
            "keyword": f"%{query}%",
            "orderby": ["last_name", "first_name"],
            "dboperation": "search_titlename",
            "limit1": 0,
            "limit2": 10,
            "displaymode": "Search",
            "ptstatus": "active",
            "fromMessenger": "False",
            "outofdomain": ""
        }
        response = self.session.post(url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all(class_="odd") + soup.find_all(class_="even")
        return table
