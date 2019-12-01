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
#include <QJsonArray>
#include <QJsonParseError>
#include <QMessageBox>
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

    void on_btCarregar_clicked();

    void on_btHome_clicked(bool checked);

    void on_btGO_clicked();

    void on_btCycStart_clicked();

    void on_homeMck_clicked();

    void on_activePrgMck_clicked();

    void on_btAtualizar_clicked();

    void on_btAlterar_clicked();

private:
    Ui::MainWindow *ui;

    //BBB State Machine
    bool homed = false;
    bool homing = false;
    bool turnedOn = false;
    bool programActive = false;
    bool programExec = false;
    bool taskExec = false;
    bool inspection = false;

    //State Machine GUI
    int stateNow = STANDBY;
    int stateOld = READY;

    //Connection Variables
    ConnectionPrompt* connectionWindow;
    bool connectionState = false;
    QString beagleBoneIP = "127.0.0.1";
    int beagleBonePort = 10000;
    QTcpSocket* tcpSocket;
    QByteArray dataBuffer;
    QJsonObject recieverObject;

    //Program Editor Variables
    int editorLinePointer = 0;
    QTableWidgetItem *cellPtr;

    //Inspection Variables
    int standardCalibration = 0;

};
#endif // MAINWINDOW_H