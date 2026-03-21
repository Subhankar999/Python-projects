import os
import pandas as pd
f1=input(" Enter file name to Create a file / use existing file :")

class student:

    def adding(self):
        data = {
            "Registration_no": int(input("Enter Registration number: ")),
            "Name": input("Enter name: ").upper(),
            "Roll": int(input("Enter roll: ")),
            "Date_of_birth": input("Enter DOB: "),
            "Gender": input("Enter gender: "),
            "Department": input("Enter dept: "),
            "Year&sem": input("Enter year & sem: "),
            "Contact_no": input("Enter contact: "),
            "Guardian_contact_no": input("Enter guardian contact: "),
            "Address": input("Enter address: ")
        }
        try:
            df = pd.read_csv(f1)
        except FileNotFoundError:
            df = pd.DataFrame(columns=data.keys())

      
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv("student.csv", index=False)

        print("Student added successfully")

    def deleting(self, reg_id):
        df = pd.read_csv("student.csv")

        if df[df["Registration_no"] == reg_id].empty:
            print("Student info not found")
        else:
            p = input("Student found. Delete? (Y/N): ").upper()
            if p == "Y":
                df.drop(df[df["Registration_no"]==reg_id].index,inplace=True)
                df.to_csv("student.csv", index=False)
                print("Deleted successfully")
            else:
                print("Cancelled")

    def searching(self, reg):
        df = pd.read_csv(f1)
        d = df[df["Registration_no"] == reg]

        if d.empty:
            print("Student not found")
        else:
            print(d)

    def updating(self, reg1):
        df = pd.read_csv("student.csv")

        if df[df["Registration_no"] == reg1].empty:
            print("Student not found")
            return

        print("""Choose field to update:
1.Name  2.Roll  3.DOB  4.Gender  5.Department
6.Year&Sem  7.Contact  8.Guardian Contact  9.Address""")

        c1 = int(input("Enter choice: "))

        idx = df[df["Registration_no"] == reg1].index

        if c1 == 1:
            df.loc[idx, "Name"] = input("Enter name: ").upper()
        elif c1 == 2:
            df.loc[idx, "Roll"] = int(input("Enter roll: "))
        elif c1 == 3:
            df.loc[idx, "Date_of_birth"] = input("Enter DOB: ")
        elif c1 == 4:
            df.loc[idx, "Gender"] = input("Enter gender: ")
        elif c1 == 5:
            df.loc[idx, "Department"] = input("Enter dept: ")
        elif c1 == 6:
            df.loc[idx, "Year&sem"] = input("Enter year & sem: ")
        elif c1 == 7:
            df.loc[idx, "Contact_no"] = input("Enter contact: ")
        elif c1 == 8:
            df.loc[idx, "Guardian_contact_no"] = input("Enter guardian contact: ")
        elif c1 == 9:
            df.loc[idx, "Address"] = input("Enter address: ")
        else:
            print("Invalid choice")
            return

        df.to_csv(f1, index=False)
        print("Updated successfully")

    def showdetails(self):
        try:
            df = pd.read_csv(f1)
            print(df)
        except FileNotFoundError:
            print("No data available")

x = student()

print("******** Student Management System ********")

while True:
    print("\n1.Add  2.Search  3.Update  4.Delete  5.Show  6.Exit")
    choice = int(input("Enter choice: "))

    if choice == 1:
        x.adding()

    elif choice == 2:
        reg = int(input("Enter registration number: "))
        x.searching(reg)

    elif choice == 3:
        reg1 = int(input("Enter registration number: "))
        x.updating(reg1)

    elif choice == 4:
        reg = int(input("Enter registration number: "))
        x.deleting(reg)

    elif choice == 5:
        x.showdetails()

    elif choice == 6:
        break

    else:
        print("Invalid choice")