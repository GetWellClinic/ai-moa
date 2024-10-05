def get_patient_html(self, type_of_query, query):
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

    def get_provider_list_from_emr_filemode(self):
        file_path = 'providers.csv'
        data = []
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transformed_row = {
                        "lastname": row["last_name"],
                        "firstname": row["first_name"],
                        "provider_number": int(row["provider_no"])
                    }
                    data.append(transformed_row)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except IOError as e:
            print(f"Error reading the file: {e}")
        return data
