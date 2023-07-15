import gspread
import json

# Указываем путь к JSON
gc = gspread.service_account(filename='autoreg_google_api_key.json')
# Открываем таблицу
sh = gc.open("Autoreg base")
worksheet = sh.sheet1


test_report = [["profile name", "uuid", "date", "time", "proxy geo", "phone geo", "billing", "status", "note", "login",
               "pass", "card", "work time", "debug code"], "123\n123\n111\n222"]


def reports_to_db(reports_list):
    rep_list = []
    codes_list = []
    for report in reports_list:
        rep_list.append(report[0])
        codes_list.append(report[1])
    # print(rep_list)
    # print(codes_list)
    with open("google_db.json", 'r') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        last_line = file_data["last_line"]
    print("last line: ", last_line)
    cell_range = 'A{}:N{}'.format(last_line, last_line + len(rep_list))
    worksheet.update(cell_range, rep_list)
    last_l = last_line
    for code in codes_list:
        worksheet.insert_note("J{}".format(last_l), code)
        last_l += 1
    file_data["last_line"] = (last_line + len(rep_list))
    print(file_data["last_line"])
    with open("google_db.json", 'w') as file:
        json.dump(file_data, file)


# reports_to_db([test_report])

