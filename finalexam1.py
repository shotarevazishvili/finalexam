import sqlite3
from PyQt5 import QtWidgets
from final_design3 import Ui_MainWindow


from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QValueAxis

from PyQt5.QtChart import QPieSeries



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connect_buttons()
        self.load_team_tables()

    def set_selected_player(self, target_lineedit):
        current_item = self.ui.listWidget.currentItem()
        if current_item:
            selected_name = current_item.text()
            target_lineedit.setText(selected_name)
        else:
            QtWidgets.QMessageBox.warning(self, "გაფრთხილება", "გთხოვ აირჩიე ფეხბურთელი სიიდან.")


    def search_players(self):
        nationality = self.ui.lineEdit_78.text().strip()
        position = self.ui.lineEdit_79.text().strip()

        conn = sqlite3.connect("finaluri.db")
        cursor = conn.cursor()

        self.ui.listWidget.clear()

        try:
            cursor.execute("""
                SELECT Name FROM players_cleaned2
                WHERE Nation = ? AND Position = ?
            """, (nationality, position))

            rows = cursor.fetchall()

            if rows:
                for (full_name,) in rows:
                    self.ui.listWidget.addItem(full_name)
            else:
                self.ui.listWidget.addItem("შედეგი ვერ მოიძებნა")

        except Exception as e:
            self.ui.listWidget.addItem(f"შეცდომა: {str(e)}")
        finally:
            conn.close()

    def save_team(self):
        team_name = self.ui.lineEdit_80.text().strip()

        if not team_name:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ, შეიყვანე გუნდის სახელი.")
            return

        table_name = team_name.replace(" ", "_")
        current_page = self.ui.stackedWidget_2.currentIndex()

        lineedits = []

        for i in range(self.ui.stackedWidget_2.count()):
            page = self.ui.stackedWidget_2.widget(i)
            if i == current_page:
                lineedits = page.findChildren(QtWidgets.QLineEdit)
                break

        player_names = list({le.text().strip() for le in lineedits if le.text().strip()})

        if len(player_names) != 11:
            QtWidgets.QMessageBox.warning(self, "შეცდომა",
                                          f"უნდა იყოს ზუსტად 11 ფეხბურთელი. ნაპოვნია: {len(player_names)}")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"DROP TABLE IF EXISTS '{table_name}'")

            cursor.execute(f"""
                CREATE TABLE '{table_name}' AS 
                SELECT * FROM players_cleaned2 WHERE 0
            """)

            for name in player_names:
                cursor.execute("""
                    INSERT INTO '{}'
                    SELECT * FROM players_cleaned2 WHERE Name = ?
                """.format(table_name), (name,))

            conn.commit()
            QtWidgets.QMessageBox.information(self, "წარმატება", f"გუნდი '{team_name}' შენახულია წარმატებით!")
            self.load_team_tables()


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"მოხდა შეცდომა: {str(e)}")

        finally:
            conn.close()

    def show_team_statistics(self):
        team_table = self.ui.comboBox.currentText()

        if not team_table:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ აირჩიე გუნდი ComboBox-იდან.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            def get_best_player(order_by, reverse=False):
                query = f"SELECT Name, {order_by} FROM '{team_table}' ORDER BY {order_by} {'DESC' if reverse else 'ASC'} LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchone()
                return f"{result[0]} ({order_by}: {result[1]})" if result else "ვერ მოიძებნა"

            self.ui.label_100.setText(get_best_player("OVR", reverse=True))
            self.ui.label_101.setText(get_best_player("Age", reverse=False))
            self.ui.label_104.setText(get_best_player("Age", reverse=True))
            self.ui.label_105.setText(get_best_player("PAC", reverse=True))
            self.ui.label_106.setText(get_best_player("DRI", reverse=True))
            self.ui.label_107.setText(get_best_player("PHY", reverse=True))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"შეცდომა მოხდა: {str(e)}")
        finally:
            conn.close()

    def load_team_tables(self):
        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]

            team_tables = [name for name in all_tables if name != "players_cleaned2" and not name.startswith("sqlite_")]

            self.ui.comboBox.clear()
            self.ui.comboBox_2.clear()
            self.ui.comboBox_3.clear()

            self.ui.comboBox.addItems(team_tables)
            self.ui.comboBox_2.addItems(team_tables)
            self.ui.comboBox_3.addItems(team_tables)
            self.ui.comboBox_4.clear()
            self.ui.comboBox_4.addItems(team_tables)
            self.ui.comboBox_5.clear()
            self.ui.comboBox_5.addItems(team_tables)



        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"ცხრილების ჩატვირთვის შეცდომა: {str(e)}")

        finally:
            conn.close()

    def show_team_statistics(self):
        team_table = self.ui.comboBox.currentText()

        if not team_table:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ აირჩიე გუნდი ComboBox-იდან.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            def get_best_player(order_by, reverse=False):
                query = f"SELECT Name, {order_by} FROM '{team_table}' ORDER BY {order_by} {'DESC' if reverse else 'ASC'} LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchone()
                return f"{result[0]} ({order_by}: {result[1]})" if result else "ვერ მოიძებნა"

            self.ui.label_100.setText(get_best_player("OVR", reverse=True))  # საუკეთესო საერთო
            self.ui.label_101.setText(get_best_player("Age", reverse=False))  # ყველაზე ახალგაზრდა
            self.ui.label_104.setText(get_best_player("Age", reverse=True))  # ყველაზე მოხუცი
            self.ui.label_105.setText(get_best_player("PAC", reverse=True))  # ყველაზე სწრაფი
            self.ui.label_106.setText(get_best_player("DRI", reverse=True))  # ყველაზე ტექნიკური
            self.ui.label_107.setText(get_best_player("PHY", reverse=True))  # ყველაზე ფიზიკურად ძლიერი

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"შეცდომა მოხდა: {str(e)}")
        finally:
            conn.close()

    def draw_team_summary_chart(self):
        team_table = self.ui.comboBox.currentText().strip()

        if not team_table:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ, აირჩიე გუნდი ComboBox-დან.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT 
                    ROUND(AVG(PAC), 1), ROUND(AVG(SHO), 1), ROUND(AVG(PAS), 1), ROUND(AVG(DRI), 1), 
                    ROUND(AVG(DEF), 1), ROUND(AVG(PHY), 1), ROUND(AVG(Age), 1)
                FROM '{team_table}'
            """)
            row = cursor.fetchone()

            if not row or all(v is None for v in row):
                QtWidgets.QMessageBox.warning(self, "ცარიელი გუნდი", "ცხრილში მოთამაშეები არ მოიძებნა.")
                return

            categories_ka = ["სისწრაფე", "დარტყმა", "პასი", "დრიბლინგი", "დაცვა", "ფიზიკა", "საშ. ასაკი"]
            values = list(row)

            bar_set = QBarSet("საშუალო მახასიათებლები")
            bar_set.append(values)

            series = QBarSeries()
            series.append(bar_set)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle(f"{team_table} - გუნდის საშუალო მახასიათებლები")
            chart.setAnimationOptions(QChart.SeriesAnimations)

            axis_x = QBarCategoryAxis()
            axis_x.append(categories_ka)

            axis_y = QValueAxis()
            axis_y.setTitleText("საშუალო მნიშვნელობა")
            axis_y.setLabelFormat("%.1f")

            chart.addAxis(axis_x, Qt.AlignBottom)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)

            layout = self.ui.widget.layout()
            if not layout:
                layout = QtWidgets.QVBoxLayout()
                self.ui.widget.setLayout(layout)

            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            layout.addWidget(chart_view)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"ჩარტის შექმნის შეცდომა: {str(e)}")

        finally:
            conn.close()

    def draw_nation_pie_chart(self):
        team_table = self.ui.comboBox.currentText().strip()

        if not team_table:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ აირჩიე გუნდი ComboBox-დან.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT Nation, COUNT(*) 
                FROM '{team_table}' 
                GROUP BY Nation
            """)
            data = cursor.fetchall()

            if not data:
                QtWidgets.QMessageBox.warning(self, "ცარიელი გუნდი", "ეროვნებები ვერ მოიძებნა ცხრილში.")
                return

            series = QPieSeries()
            for nation, count in data:
                series.append(f"{nation} ({count})", count)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("გუნდის ეროვნული შემადგენლობა")
            chart.legend().setAlignment(Qt.AlignRight)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)

            layout = self.ui.widget_2.layout()
            if not layout:
                layout = QtWidgets.QVBoxLayout()
                self.ui.widget_2.setLayout(layout)

            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            layout.addWidget(chart_view)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"ეროვნებების დიაგრამის შეცდომა: {str(e)}")
        finally:
            conn.close()

    def compare_teams_chart(self):
        team1 = self.ui.comboBox_2.currentText().strip()
        team2 = self.ui.comboBox_3.currentText().strip()

        if not team1 or not team2:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ აირჩიე ორივე გუნდი.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            def get_team_totals(table):
                cursor.execute(f"""
                    SELECT 
                        SUM(PAC), SUM(SHO), SUM(PAS), SUM(DRI), 
                        SUM(DEF), SUM(PHY), ROUND(AVG(Age), 1)
                    FROM '{table}'
                """)
                return list(cursor.fetchone())

            stats1 = get_team_totals(team1)
            stats2 = get_team_totals(team2)

            if not stats1 or not stats2:
                QtWidgets.QMessageBox.warning(self, "შეცდომა", "ერთ-ერთ გუნდში არ მოიძებნა მონაცემი.")
                return

            categories_ka = ["სისწრაფე", "დარტყმა", "პასი", "დრიბლინგი", "დაცვა", "ფიზიკა", "საშ. ასაკი"]

            bar1 = QBarSet(team1)
            bar1.append(stats1)

            bar2 = QBarSet(team2)
            bar2.append(stats2)

            series = QBarSeries()
            series.append(bar1)
            series.append(bar2)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("გუნდების შედარება")
            chart.setAnimationOptions(QChart.SeriesAnimations)

            axis_x = QBarCategoryAxis()
            axis_x.append(categories_ka)

            axis_y = QValueAxis()
            axis_y.setLabelFormat("%.0f")

            chart.addAxis(axis_x, Qt.AlignBottom)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)

            layout = self.ui.widget_3.layout()
            if not layout:
                layout = QtWidgets.QVBoxLayout()
                self.ui.widget_3.setLayout(layout)

            for i in reversed(range(layout.count())):
                item = layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            layout.addWidget(chart_view)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"შედარების დიაგრამის შეცდომა: {str(e)}")
        finally:
            conn.close()

    def delete_selected_team_table(self):
        team_table = self.ui.comboBox_4.currentText().strip()

        if not team_table:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "გთხოვ, აირჩიე გუნდი წასაშლელად.")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "დადასტურება",
            f"დარწმუნებული ხარ რომ გინდა '{team_table}' წაშლა?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"DROP TABLE IF EXISTS '{team_table}'")
            conn.commit()

            QtWidgets.QMessageBox.information(self, "წარმატება", f"'{team_table}' წარმატებით წაიშალა.")
            self.load_team_tables()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"წაშლის შეცდომა: {str(e)}")

        finally:
            conn.close()

    def load_players_for_selected_team(self):
        team_table = self.ui.comboBox_5.currentText().strip()

        self.ui.listWidget_2.clear()

        if not team_table:
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"SELECT Name FROM '{team_table}'")
            rows = cursor.fetchall()

            for (name,) in rows:
                self.ui.listWidget_2.addItem(name)

        except Exception as e:
            self.ui.listWidget_2.addItem(f"შეცდომა: {str(e)}")

        finally:
            conn.close()

    def delete_selected_player(self):
        team_table = self.ui.comboBox_5.currentText().strip()
        current_item = self.ui.listWidget_2.currentItem()

        if not team_table or not current_item:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "აირჩიე გუნდი და ფეხბურთელი.")
            return

        player_name = current_item.text()

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute(f"DELETE FROM '{team_table}' WHERE Name = ?", (player_name,))
            conn.commit()

            QtWidgets.QMessageBox.information(self, "წარმატება", f"'{player_name}' წაიშალა გუნდიდან.")
            self.load_players_for_selected_team()  # განაახლე სია

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"წაშლის შეცდომა: {str(e)}")

        finally:
            conn.close()

    def add_new_player_to_team(self):
        team_table = self.ui.comboBox_5.currentText().strip()
        new_player = self.ui.lineEdit_81.text().strip()

        if not team_table or not new_player:
            QtWidgets.QMessageBox.warning(self, "შეცდომა", "შეიყვანე გუნდი და ახალი ფეხბურთელი.")
            return

        try:
            conn = sqlite3.connect("finaluri.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM players_cleaned2 WHERE Name = ?", (new_player,))
            player_data = cursor.fetchone()

            if not player_data:
                QtWidgets.QMessageBox.warning(self, "ვერ მოიძებნა", f"'{new_player}' არ მოიძებნა ბაზაში.")
                return

            placeholders = ",".join(["?"] * len(player_data))
            cursor.execute(f"INSERT INTO '{team_table}' VALUES ({placeholders})", player_data)
            conn.commit()

            QtWidgets.QMessageBox.information(self, "წარმატება", f"'{new_player}' დაემატა გუნდს.")
            self.load_players_for_selected_team()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "შეცდომა", f"დამატების შეცდომა: {str(e)}")

        finally:
            conn.close()

    def connect_buttons(self):
        self.ui.pushButton.clicked.connect(self.search_players)

        # ფორმაციის გგვერდებზე გადართვა
        self.ui.pushButton_31.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))  # page_6
        self.ui.pushButton_32.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))  # page_8
        self.ui.pushButton_19.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(3))  # page_4
        self.ui.pushButton_27.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(4))  # page_9
        self.ui.pushButton_28.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(5))  # page_7
        self.ui.pushButton_29.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(6))  # page_5
        self.ui.pushButton_30.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))  # page_3
        self.ui.pushButton_25.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(6))  # page_5
        self.ui.pushButton_26.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))  # page_3
        self.ui.pushButton_20.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))  # page_6
        self.ui.pushButton_21.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))  # page_8
        self.ui.pushButton_22.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(3))  # page_4
        self.ui.pushButton_23.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(4))  # page_9
        self.ui.pushButton_24.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(5))  # page_7

        # მთავარი  გვერდებზე გადართვა:
        self.ui.pushButton_16.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.pushButton_15.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.pushButton_17.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_7.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))





        self.ui.pushButton_8.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_56))
        self.ui.pushButton_12.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_69))
        self.ui.pushButton_36.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_68))
        self.ui.pushButton_11.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_70))
        self.ui.pushButton_13.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_71))
        self.ui.pushButton_14.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_72))
        self.ui.pushButton_9.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_75))
        self.ui.pushButton_10.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_74))
        self.ui.pushButton_34.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_73))
        self.ui.pushButton_33.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_76))
        self.ui.pushButton_35.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_77))
        self.ui.pushButton_41.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_34))
        self.ui.pushButton_40.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_35))
        self.ui.pushButton_39.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_38))
        self.ui.pushButton_38.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_36))
        self.ui.pushButton_37.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_37))
        self.ui.pushButton_46.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_39))
        self.ui.pushButton_42.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_40))
        self.ui.pushButton_43.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_41))
        self.ui.pushButton_45.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_42))
        self.ui.pushButton_44.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_43))
        self.ui.pushButton_47.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_44))
        self.ui.pushButton_54.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_13))
        self.ui.pushButton_55.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_12))
        self.ui.pushButton_57.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_15))
        self.ui.pushButton_52.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_14))
        self.ui.pushButton_56.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_19))
        self.ui.pushButton_53.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_16))
        self.ui.pushButton_51.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_20))
        self.ui.pushButton_50.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_21))
        self.ui.pushButton_49.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_22))
        self.ui.pushButton_48.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_18))
        self.ui.pushButton_58.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_17))
        self.ui.pushButton_68.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_23))
        self.ui.pushButton_69.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_25))
        self.ui.pushButton_67.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_26))
        self.ui.pushButton_62.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_28))
        self.ui.pushButton_61.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_29))
        self.ui.pushButton_66.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_24))
        self.ui.pushButton_60.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_27))
        self.ui.pushButton_59.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_32))
        self.ui.pushButton_65.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_31))
        self.ui.pushButton_64.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_30))
        self.ui.pushButton_63.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_33))
        self.ui.pushButton_73.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_49))
        self.ui.pushButton_72.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_48))
        self.ui.pushButton_74.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_51))
        self.ui.pushButton_75.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_52))
        self.ui.pushButton_71.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_50))
        self.ui.pushButton_70.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_53))
        self.ui.pushButton_80.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_47))
        self.ui.pushButton_77.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_46))
        self.ui.pushButton_79.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_45))
        self.ui.pushButton_76.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_55))
        self.ui.pushButton_78.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_54))
        self.ui.pushButton_86.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_59))
        self.ui.pushButton_85.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_64))
        self.ui.pushButton_83.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_63))
        self.ui.pushButton_84.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_62))
        self.ui.pushButton_91.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_61))
        self.ui.pushButton_90.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_60))
        self.ui.pushButton_87.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_65))
        self.ui.pushButton_82.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_66))
        self.ui.pushButton_81.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_67))
        self.ui.pushButton_88.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_58))
        self.ui.pushButton_89.clicked.connect(lambda: self.set_selected_player(self.ui.lineEdit_57))

        self.ui.pushButton_2.clicked.connect(self.save_team)

        self.ui.pushButton_3.clicked.connect(self.show_team_statistics)

        self.ui.pushButton_3.clicked.connect(self.draw_team_summary_chart)
        self.ui.pushButton_3.clicked.connect(self.draw_nation_pie_chart)

        self.ui.pushButton_18.clicked.connect(self.compare_teams_chart)

        self.ui.pushButton_4.clicked.connect(self.delete_selected_team_table)

        self.ui.comboBox_5.currentTextChanged.connect(self.load_players_for_selected_team)

        self.ui.pushButton_5.clicked.connect(self.delete_selected_player)

        self.ui.pushButton_6.clicked.connect(self.add_new_player_to_team)










if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




