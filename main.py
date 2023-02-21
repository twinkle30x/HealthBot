from datetime import datetime, timedelta
import speech_recognition as sr
import time
from prettytable import PrettyTable
import pymysql
import random
import calendar

Ros_pal = "\033[38:5:181m"
Rcheck = "\033[38:5:120m"
Rv = "\033[38:5:189m"
Rg = "\033[38:5:194m"
Rr = "\033[38:5:225m"
R = "\u001b[31m"
print(Rv)
connection = pymysql.connect(host="localhost", user="root", passwd="", database="healthbot")
cursor = connection.cursor()


def showMenu():
    print(Rg)
    print("1. Check environment and patient status")
    print("2. Show all patients")
    print("3. Show data based on: day, week, month, year")
    print("4. Exit")
    print(Rv)


class Environment(object):
    def __init__(self, airpollution, temperature, co, waterquality, date):
        self.temperature = temperature
        self.co = co
        self.waterquality = waterquality
        self.airpollution = airpollution
        self.date = date

    def showStatus(self):
        table = [['Environment', 'value'], ['temperature:', self.temperature], ['air pollution:', self.airpollution],
                 ['co level:', self.co], ['water quality:', self.waterquality], ['date:', self.date]]
        tab = PrettyTable(table[0])
        tab.add_rows(table[1:])
        print(Rr, tab)


class Pacient(object):
    def __init__(self, temperature, bloodpressure, disease, disease2, date):
        self.temperature = temperature
        self.bloodpressure = bloodpressure
        self.disease = disease
        self.disease2 = disease2
        self.date = date

    def showStatus(self):
        table = [['Patient', 'value'], ['temperature:', self.temperature], ['blood pressure:', self.bloodpressure],
                 ['disease1:', self.disease], ['disease2:', self.disease2], ['date:', self.date]]

        tab = PrettyTable(table[0])
        tab.add_rows(table[1:])
        print(Rr, tab)


def saveData():
    maxim_value = 21
    id_count = cursor.execute("SELECT `id` FROM `patient`")
    if (id_count > maxim_value):
        print(R, "Too many patients, create another file or delete unused data")
        print(Rg)
    else:
        cursor.execute(
            "INSERT INTO `environment` (`airpollution`, `temperature`, `co`, `waterquality`, `date`) VALUES (%s, %s, %s, %s, %s)",
            (airpollution, temp_envi, co, waterquality, date))
        connection.commit()
        cursor.execute(
            "INSERT INTO `patient` (`temperature`, `bloodpressure`, `disease`, `disease2`, `date`) VALUES (%s, %s, %s, %s, %s);",
            (temp_user, bloodpressure, disease1, disease2, date))
        connection.commit()
        print(Rr, "Environment and Patient has been registered.")


def showAllPacients():
    retrive = "Select * From patient;"
    cursor.execute(retrive)
    rows = cursor.fetchall()
    for row in rows:
        print(Rr, row)


def getDataFromToday(date):
    print(Rg, "Environments:")
    cursor.execute("SELECT * FROM environment WHERE date = %s;", date)
    rows1 = cursor.fetchall()
    for row in rows1:
        print(row)
    print(Rg, "Patients:")
    cursor.execute("SELECT * FROM patient WHERE date = %s;", date)
    connection.commit()
    rows2 = cursor.fetchall()
    for row in rows2:
        print(Rr, row)


def getDataFromWeek(start, end):
    print(Rg, "Environments:")
    cursor.execute("SELECT * FROM environment where date >= %s and date <= %s;", (str(start), str(end)))
    connection.commit()
    rows1 = cursor.fetchall()
    for row in rows1:
        print(Rr, row)
    print(Rg, "Patients:")
    cursor.execute("SELECT * FROM patient where date >= %s and date <= %s;", (str(start), str(end)))
    connection.commit()
    rows2 = cursor.fetchall()
    for row in rows2:
        print(Rr, row)


def getDataFromMonth(first_day_of_month, last_day_of_month):
    print(Rg, "Environments:")
    cursor.execute("SELECT * FROM environment where date >= %s and date < %s;",
                   (str(first_day_of_month), str(last_day_of_month)))
    rows1 = cursor.fetchall()
    for row in rows1:
        print(Rr, row)
    print(Rg, "Patients:")
    cursor.execute("SELECT * FROM patient where date >= %s and date < %s;",
                   (str(first_day_of_month), str(last_day_of_month)))
    connection.commit()
    rows2 = cursor.fetchall()
    for row in rows2:
        print(Rr, row)


def getDataFromYear(first_day_of_year, last_day_of_year):
    print(Rg, "Environments:")
    cursor.execute("SELECT * FROM environment where date >= %s and date < %s;",
                   (str(first_day_of_year), str(last_day_of_year)))
    rows1 = cursor.fetchall()
    for row in rows1:
        print(Rr,row)
    print(Rg, "Patients:")
    cursor.execute("SELECT * FROM patient where date >= %s and date < %s;",
                   (str(first_day_of_year), str(last_day_of_year)))
    connection.commit()
    rows2 = cursor.fetchall()
    for row in rows2:
        print(Rr, row)


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def findWaitingTime(processes, n, bt, wt):
    # waiting time for
    # first process is 0
    wt[0] = 0

    # calculating waiting time
    for i in range(1, n):
        wt[i] = bt[i - 1] + wt[i - 1]


# Function to calculate turn
# around time
def findTurnAroundTime(processes, n,
                       bt, wt, tat):
    # calculating turnaround
    # time by adding bt[i] + wt[i]
    for i in range(n):
        tat[i] = bt[i] + wt[i]


# Function to calculate
# average time
def findavgTime(processes, n, bt):
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    # Function to find waiting
    # time of all processes
    findWaitingTime(processes, n, bt, wt)

    # Function to find turn around
    # time for all processes
    findTurnAroundTime(processes, n,
                       bt, wt, tat)

    # Display processes along
    # with all details
    print("Processes Burst time " +
          " Waiting time " +
          " Turn around time")

    # Calculate total waiting time
    # and total turn around time
    for i in range(n):
        total_wt = total_wt + wt[i]
        total_tat = total_tat + tat[i]
        print(" " + str(i + 1) + "\t\t" +
              str(bt[i]) + "\t " +
              str(wt[i]) + "\t\t " +
              str(tat[i]))

    print("Average waiting time = " +
          str(total_wt / n))
    print("Average turn around time = " +
          str(total_tat / n))


if __name__ == '__main__':
    start = time.time()
    print("How would you like to interact with the HealthBot?")
    op = int(input("1. I'll enter by myself the options\n2. I'll talk to him\n"))

    if int(op) == 1:
        showMenu()

        option_text = int(input("Enter the number for your choice: "))
        while option_text < 4:

            choices_text = ["low", "medium", "high"]
            qualiy_text = ["poor", "decent", "good"]
            diseasesNames_text1 = ["Flu", "Cancer", "COVID-19", "HIV", "Lupus"]
            diseasesNames_text2 = ["ChickenPox", "Depression", "Chlamydia", "Ebola", "Conjunctivitis"]

            date = datetime.now().date()

            if (option_text == 1):
                temp_envi = random.randint(0, 30)
                airpollution = random.choice(choices_text)
                co = random.choice(choices_text)
                waterquality = random.choice(qualiy_text)

                temp_user = random.randint(0, 50)
                bloodpressure = random.choice(choices_text)
                disease1 = random.choice(diseasesNames_text1)
                disease2 = random.choice(diseasesNames_text2)

                env = Environment(airpollution, str(temp_envi), co, waterquality, str(date))
                env.showStatus()
                print()
                patient = Pacient(str(temp_user), bloodpressure, disease1, disease2, str(date))
                patient.showStatus()
                print(Rg, "Would you like to save data? \n 1. yes \n 2. generate new one\n")
                code_text = int(input("Enter the number for your choice: "))
                time.sleep(1)
                if (code_text == 1):
                    saveData()
                else:
                    continue
            elif (option_text == 2):
                showAllPacients()
            elif (option_text == 3):
                print(("1. day\n 2. weekly\n 3. month\n 4. year\n"))

                val_text = int(input("Enter the number for your choice: "))
                if (val_text == 1):
                    getDataFromToday(date)
                elif (val_text == 2):
                    day = str(date)
                    dt = datetime.strptime(str(day), '%Y-%m-%d')
                    start = dt - timedelta(days=dt.weekday())
                    end = start + timedelta(days=6)
                    getDataFromWeek(start, end)

                elif (val_text == 3):
                    first_day_of_month = date.strftime("%Y-%m-01")
                    last_day_of_month = d = date.replace(day=calendar.monthrange(date.year, date.month)[1])
                    getDataFromMonth(first_day_of_month, last_day_of_month)

                elif (val_text == 4):
                    first_day_of_year = datetime.now().date().replace(month=1, day=1)
                    last_day_of_year = datetime.now().date().replace(month=12, day=31)
                    getDataFromYear(first_day_of_year, last_day_of_year)
            print()
            showMenu()
            option_text = int(input("Enter the number for your choice: "))

    else:
        showMenu()

        print("Say the number for your choice: ")
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        option_speech = recognize_speech_from_mic(recognizer, microphone)
        print("You said: {}".format(option_speech["transcription"]))
        time.sleep(3)

        while option_speech["transcription"] < "4":

            choices_speech = ["low", "medium", "high"]
            qualiy_speech = ["poor", "decent", "good"]
            diseasesNames_speech1 = ["Flu", "Cancer", "COVID-19", "HIV", "Lupus"]
            diseasesNames_speech2 = ["ChickenPox", "Depression", "Chlamydia", "Ebola", "Conjunctivitis"]

            date = datetime.now().date()

            if (option_speech["transcription"] == "1"):
                temp_env = random.randint(0, 30)
                airpollution = random.choice(choices_speech)
                co = random.choice(choices_speech)
                waterquality = random.choice(qualiy_speech)

                temp_user = random.randint(0, 50)
                bloodpressure = random.choice(choices_speech)
                disease1 = random.choice(diseasesNames_speech1)
                disease2 = random.choice(diseasesNames_speech2)

                env = Environment(airpollution, str(temp_env), co, waterquality, str(date))
                env.showStatus()
                print()
                patient = Pacient(str(temp_user), bloodpressure, disease1, disease2, str(date))
                patient.showStatus()
                print("Would you like to save data? \n 1. yes \n 2. generate new one\n")
                rec = sr.Recognizer()
                mic = sr.Microphone()
                code = recognize_speech_from_mic(rec, mic)
                time.sleep(1)
                if (code["transcription"] == "yes"):
                    saveData()
                else:
                    continue
            elif (option_speech["transcription"] == "2"):
                showAllPacients()
            elif (option_speech["transcription"] == "3"):
                print(("1. day\n 2. weekly\n 3. month\n 4. year\n"))
                print(Rv, "Say your choice: ")
                rec2 = sr.Recognizer()
                mic2 = sr.Microphone()
                val = recognize_speech_from_mic(rec2, mic2)
                if (val["transcription"] == "day"):
                    getDataFromToday(date)
                elif (val["transcription"] == "weekly"):
                    day = str(date)
                    dt = datetime.strptime(str(day), '%Y-%m-%d')
                    start = dt - timedelta(days=dt.weekday())
                    end = start + timedelta(days=6)
                    getDataFromWeek(start, end)

                elif (val["transcription"] == "month"):
                    first_day_of_month = date.strftime("%Y-%m-01")
                    last_day_of_month = d = date.replace(day=calendar.monthrange(date.year, date.month)[1])
                    getDataFromMonth(first_day_of_month, last_day_of_month)

                elif (val["transcription"] == "year"):
                    first_day_of_year = datetime.now().date().replace(month=1, day=1)
                    last_day_of_year = datetime.now().date().replace(month=12, day=31)
                    getDataFromYear(first_day_of_year, last_day_of_year)
            print()
            showMenu()
            print("Say the number for your choice: ")
            rec3 = sr.Recognizer()
            mic3 = sr.Microphone()
            option_speech = recognize_speech_from_mic(rec3, mic3)
            print("You said: {}".format(option_speech["transcription"]))

    stop = time.time()
    print("Running time: ", stop - start)
connection.close()
