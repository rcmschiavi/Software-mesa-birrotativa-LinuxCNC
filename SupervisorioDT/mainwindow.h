#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#define EXTESTOP -2
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
#define VELOC 3
#define FIM_OP 4
#define INSPECT 5

#include <QMainWindow>
#include <QTcpSocket>
#include <QHostAddress>
#include <QTableWidget>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QJsonParseError>
#include <QFileDialog>
#include <QFile>
#include <QMessageBox>
#include <QSettings>
#include <QCloseEvent>
#include <QImageReader>
#include <QBuffer>
#include "connectionprompt.h"


QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    //Construtor e Destrutor
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

public slots:
    //Close Event
    void closeEvent(QCloseEvent *event);

    //Configurações de IP da janela externa.
    void saveIpConfiguration(QString IP);
    void savePortConfiguration(int port);

    //Slots conectados a ações no menu dropdown.
    void openFileAct();
    void saveFileAct();
    void aboutSupervisorio();

private slots:

    //Configurações de Conexão
    void on_btConfig_clicked();
    void onReadyRead();
    void disconnectHandler();

    //Wrappers Json para TCP/IP
    void sendJsonThroughSocket(QJsonObject obj);
    QJsonDocument recieveJsonThroughSocket();

    //Funções de arquivo
    void saveJsonToFile(QJsonDocument doc);
    QJsonDocument loadJsonFromFile();
    void recieveJsonProgramFromBBB(QJsonObject program);
    void loadUserSettings();
    void saveUserSettings();

    //STATE MACHINE
    void changeWindowStatus();
    void changeWindowState(int state);
    void on_btExtEstop_clicked();
    void on_btConnect_clicked(bool checked);
    void on_btLiga_clicked(bool checked);
    void on_btEstop_clicked(bool checked);
    void on_btProgramar_clicked(bool checked);
    void on_btJogging_clicked(bool checked);
    void on_btAuto_clicked(bool checked);

    //Comandos Diretos para BBB
    //Movimento
    void on_btHome_clicked(bool checked);
    void on_btGO_clicked();
    //Programa
    void on_btCarregar_clicked();
    void on_btReceber_clicked();
    void on_btDeletar_clicked();
    void on_btCycStart_clicked();
    //Inspeção
    void on_btAtualizar_clicked();
    void on_btAlterar_clicked();

    //Funções do Warning Log
    void on_btClearLog_clicked();

    //Funções de cinemática
    double checkSpeeds(double B_ang, double C_ang, double veloc);

    //Funções do editor de programa
    void on_btAddTarefa_clicked();
    void on_btExcluir_clicked();
    void on_btLimpar_clicked();
    void drawWidgetTable(double B_ang, double C_ang, double veloc, bool fim_op, bool inspect);
    QJsonObject loadWidgetTable();
    void clearWidgetTable();

    //Handler para parâmetros do editor de programa
    void on_cbFimOp_clicked(bool checked);
    void on_cbInspecao_clicked(bool checked);
    void on_cbFimOpJog_clicked(bool checked);
    void on_cbInspecaoJog_toggled(bool checked);

    void on_cbLinear_clicked(bool checked);
    void on_cbJunta_clicked(bool checked);

    void on_cbLinearJog_clicked(bool checked);

    void on_cbJuntaJog_clicked(bool checked);

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

    //BBB Params
    //Speed deg per sec
    double B_maxSpeed=3;
    double C_maxSpeed=25;
    double B_lastPos=0;
    double C_lastPos=0;

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
    int frameBufferSize=0;
    bool recievingImage=false;

    //Program Editor Variables
    int editorLinePointer = 0;
    QTableWidgetItem *cellPtr;
    bool clearOcurred = false;

    //Inspection Variables
    int standardCalibration = 0;

};
#endif // MAINWINDOW_H
