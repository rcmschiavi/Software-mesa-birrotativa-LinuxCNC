#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#define ESTOP -1
#define STANDBY 0
#define CONNECTED_STANDBY 1
#define READY 2
#define JOG 3
#define PROG 4
#define AUTO 5
#define AUTO_RUN 6

#define TASK 0
#define B_ANG 1
#define C_ANG 2
#define FIM_OP 3
#define INSPECT 4

#include <QMainWindow>
#include <QTcpSocket>
#include <QHostAddress>
#include <QTableWidget>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>
#include "connectionprompt.h"


QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

public slots:
    void saveIpConfiguration(QString IP);
    void savePortConfiguration(int port);

private slots:
    void on_btConfig_clicked();
    void onReadyRead();

    void changeWindowState(int state);

    void on_btConnect_clicked(bool checked);

    void on_btLiga_clicked(bool checked);

    void on_btProgramar_clicked(bool checked);

    void on_btEstop_clicked(bool checked);

    void on_btClearLog_clicked();

    void on_btJogging_clicked(bool checked);

    void on_btAuto_clicked(bool checked);

    void on_btAddTarefa_clicked();

    void on_btExcluir_clicked();

    void on_btLimpar_clicked();

    void on_cbFimOp_clicked(bool checked);

    void on_cbInspecao_clicked(bool checked);


    void on_cbFimOpJog_clicked(bool checked);

    void on_cbInspecaoJog_toggled(bool checked);

    void sendJsonThroughSocket(QJsonObject obj);

    QJsonObject recieveJsonThroughSocket();

private:
    Ui::MainWindow *ui;

    //State Machine
    int stateNow = STANDBY;
    int stateOld = READY;
    bool homed = false;
    bool turnedOn = false;

    //Connection Variables
    ConnectionPrompt* connectionWindow;
    bool connectionState = false;
    QString beagleBoneIP = "127.0.0.1";
    int beagleBonePort = 10000;
    QTcpSocket* tcpSocket;
    QByteArray dataBuffer;

    //
    int editorLinePointer = 0;
    QTableWidgetItem *cellPtr;
};
#endif // MAINWINDOW_H
