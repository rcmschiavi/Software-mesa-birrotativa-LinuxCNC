#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    this->connectionWindow = new ConnectionPrompt(this);
    ui->setupUi(this);
    //Conexão de sinais e slots entre a janela principal e a janela de configuração
    connect(this->connectionWindow, SIGNAL(updateIP(QString)), this, SLOT(saveIpConfiguration(QString)));
    connect(this->connectionWindow, SIGNAL(updatePort(int)), this, SLOT(savePortConfiguration(int)));
}

MainWindow::~MainWindow()
{
    delete ui;
}

//==============================================CONNECTION==========================================

void MainWindow::saveIpConfiguration(QString IP)
{
    this->beagleBoneIP = IP;
    ui->warningLog->append("Ip: "+IP);
}

void MainWindow::savePortConfiguration(int port)
{
    this->beagleBonePort = port;
    ui->warningLog->append("Port: "+QString::number(port));
}

void MainWindow::sendJsonThroughSocket(const QJsonObject obj)
{
   QJsonDocument doc;
   doc.setObject(obj);
   QByteArray message = doc.toBinaryData();
   tcpSocket->write(message);
}

QJsonObject MainWindow::recieveJsonThroughSocket()
{
   QJsonParseError parseError;
   QJsonDocument doc = QJsonDocument::fromJson(tcpSocket->readAll(), &parseError);
   if(parseError.error == QJsonParseError::NoError)
   {
       ui->warningLog->append("Erro na conversão Json");
       QJsonObject nulo;
       return nulo;
   }
   QJsonObject obj = doc.object();
   return obj;
}

void MainWindow::on_btConfig_clicked()
{
    this->connectionWindow->show();
}

//Slot acionado sempre que exite um pacote TCP pronto para leitura.
void MainWindow::onReadyRead()
{
    this->dataBuffer = this->tcpSocket->readAll();
}

//=============================================STATE MACHINE===============================

void MainWindow::changeWindowState(int state)
{
    //Função que prepara a máquina de estados da janela.
    switch(state)
    {
    case ESTOP:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(false);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(true);
        this->stateNow = ESTOP;
        ui->stateEstado->setText("ESTOP");
        break;
    case STANDBY:
        ui->btEstop->setEnabled(false);
        ui->btLiga->setEnabled(false);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(false);
        ui->groupInspect->setEnabled(false);
        ui->groupStatus->setEnabled(false);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(false);
        this->stateNow = STANDBY;
        ui->stateEstado->setText("STANDBY");
        ui->stateConnected->setText("NÃO");
        ui->stateEstop->setText("SIM");
        ui->stateHomed->setText("NÃO");
        ui->stateTurnedOn->setText("NÃO");
        break;
    case CONNECTED_STANDBY:
        ui->btEstop->setEnabled(false);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(false);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(true);
        this->stateNow = CONNECTED_STANDBY;
        ui->stateEstado->setText("CONECTADO");
        ui->stateConnected->setText("SIM");
        break;
    case READY:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(true);
        this->stateNow = READY;
        ui->stateEstado->setText("PRONTO");
        ui->btJogging->setChecked(false);
        ui->btProgramar->setChecked(false);
        ui->btAuto->setChecked(false);
        break;
    case JOG:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(true);
        ui->groupJog->setEnabled(true);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(true);
        ui->cameraImage->setEnabled(true);
        this->stateNow = JOG;
        ui->stateEstado->setText("JOG");
        break;
    case PROG:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(true);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(true);
        ui->cameraImage->setEnabled(true);
        this->stateNow = PROG;
        ui->stateEstado->setText("PROG");
        break;
    case AUTO:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(true);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(true);
        ui->cameraImage->setEnabled(true);
        this->stateNow = AUTO;
        ui->stateEstado->setText("AUTO");
        break;
    case AUTO_RUN:
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(false);
        ui->groupInspect->setEnabled(true);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(true);
        this->stateNow = AUTO_RUN;
        ui->stateEstado->setText("RUN");
        break;
    }
}

void MainWindow::on_btConnect_clicked(bool checked)
{
    if(checked)
    {
        /*  TEST THIS AFTER DEVELOPMENT
        try
        {
            tcpSocket->connectToHost(QHostAddress(beagleBoneIP), beagleBonePort);

        }
        catch (...)
        {
            ui->btConnect->setChecked(false);
            return;
        }
        connect(this->tcpSocket, SIGNAL(readyRead()), this, SLOT(onReadyRead()));
        */
        this->connectionState = true;
        this->stateNow = CONNECTED_STANDBY;
        ui->stateConnected->setText("SIM");
        changeWindowState(CONNECTED_STANDBY);
    }
    else
    {
        if(this->stateNow == CONNECTED_STANDBY)
        {
            /*
            tcpSocket->disconnectFromHost();
            */
            this->connectionState = false;
            changeWindowState(STANDBY);
        }
        else
        {
            ui->btConnect->setChecked(true);
        }

    }
}

void MainWindow::on_btLiga_clicked(bool checked)
{
    if(checked)
    {
        if(this->stateNow == CONNECTED_STANDBY)
        {
            changeWindowState(ESTOP);
        }
        else
            ui->btLiga->setChecked(false);
    }
    else
    {
        if(this->stateNow == ESTOP)
        {
            changeWindowState(CONNECTED_STANDBY);
        }
        else
            ui->btLiga->setChecked(true);
    }
}

void MainWindow::on_btProgramar_clicked(bool checked)
{
    if(checked)
    {
        if(this->stateNow == ESTOP)
        {
            changeWindowState(PROG);
        }
        else
            ui->btProgramar->setChecked(false);
    }
    else
    {
        if(this->stateNow == PROG)
        {
            changeWindowState(ESTOP);
        }
        else
            ui->btProgramar->setChecked(true);
    }
}

void MainWindow::on_btEstop_clicked(bool checked)
{
    if(checked)
    {
        if(this->stateNow == PROG)
            return;
        changeWindowState(ESTOP);
    }
    else
    {
        if(this->stateNow == PROG)
            ui->btEstop->setChecked(true);
        else
            changeWindowState(READY);

    }
}

void MainWindow::on_btClearLog_clicked()
{
    ui->warningLog->clear();
}

void MainWindow::on_btJogging_clicked(bool checked)
{
    if(checked)
    {
        if(this->stateNow == READY)
        {
            changeWindowState(JOG);
        }
        else
            ui->btJogging->setChecked(false);
    }
    else
    {
        if(this->stateNow == JOG)
        {
            changeWindowState(READY);
        }
        else
            ui->btJogging->setChecked(true);
    }
}

void MainWindow::on_btAuto_clicked(bool checked)
{
    if(checked)
    {
        if(this->stateNow == READY)
        {
            changeWindowState(AUTO);
        }
        else
            ui->btAuto->setChecked(false);
    }
    else
    {
        if(this->stateNow == AUTO)
        {
            changeWindowState(READY);
        }
        else
            ui->btAuto->setChecked(true);
    }
}

void MainWindow::on_btAddTarefa_clicked()
{
    int auxPointer = editorLinePointer;
    double B_Value = ui->sbBProg->value();
    double C_Value = ui->sbCProg->value();
    bool fim_op = ui->cbFimOp->isChecked();
    bool inspect = ui->cbInspecao->isChecked();
    if(this->stateNow == PROG)
    {
        B_Value = ui->sbBProg->value();
        C_Value = ui->sbCProg->value();
        fim_op = ui->cbFimOp->isChecked();
        inspect = ui->cbInspecao->isChecked();
    }
    else if(this->stateNow == JOG && ui->cbTeach->isChecked())
    {
        B_Value = ui->sbBJog->value();
        C_Value = ui->sbCJog->value();
        fim_op = ui->cbFimOpJog->isChecked();
        inspect = ui->cbInspecaoJog->isChecked();
    }
    else
        return;
    editorLinePointer = ui->programEditor->currentRow();
    ui->programEditor->insertRow(editorLinePointer);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(editorLinePointer));
    ui->programEditor->setItem(editorLinePointer,TASK,cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(B_Value));
    ui->programEditor->setItem(editorLinePointer,B_ANG,cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(C_Value));
    ui->programEditor->setItem(editorLinePointer,C_ANG,cellPtr);
    if(fim_op)
    {
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("TRUE");
        ui->programEditor->setItem(editorLinePointer,FIM_OP,cellPtr);
    }
    else
    {
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("FALSE");
        ui->programEditor->setItem(editorLinePointer,FIM_OP,cellPtr);
    }
    if(inspect)
    {
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("TRUE");
        ui->programEditor->setItem(editorLinePointer,INSPECT,cellPtr);
    }
    else
    {
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("FALSE");
        ui->programEditor->setItem(editorLinePointer,INSPECT,cellPtr);
    }
    editorLinePointer = auxPointer;
    editorLinePointer++;
    for(int i=0;i<ui->programEditor->rowCount();i++)
    {
        if(ui->programEditor->item(i,TASK) != nullptr)
        {
            ui->programEditor->item(i,TASK)->setText(QString::number(i+1));
        }
    }
}

void MainWindow::on_btExcluir_clicked()
{
    if(this->stateNow == PROG || (this->stateNow == JOG && ui->cbTeach->isChecked()))
    {
        if(ui->programEditor->rowCount() != 1)
        {
            ui->programEditor->removeRow(ui->programEditor->currentRow());
            editorLinePointer = ui->programEditor->rowCount();
            for(int i=0;i<ui->programEditor->rowCount();i++)
            {
                if(ui->programEditor->item(i,TASK) != nullptr)
                {
                    ui->programEditor->item(i,TASK)->setText(QString::number(i+1));
                }
            }
        }
    }
}

void MainWindow::on_btLimpar_clicked()
{
    if(this->stateNow == PROG || (this->stateNow == JOG && ui->cbTeach->isChecked()))
    {
        ui->programEditor->clear();
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("TASK #");
        ui->programEditor->setHorizontalHeaderItem(TASK, cellPtr);
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("B");
        ui->programEditor->setHorizontalHeaderItem(B_ANG, cellPtr);
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("C");
        ui->programEditor->setHorizontalHeaderItem(C_ANG, cellPtr);
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("FIM OPERAÇÃO?");
        ui->programEditor->setHorizontalHeaderItem(FIM_OP, cellPtr);
        cellPtr = new QTableWidgetItem;
        cellPtr->setText("INSPEÇÃO?");
        ui->programEditor->setHorizontalHeaderItem(INSPECT, cellPtr);
    }
}

void MainWindow::on_cbFimOp_clicked(bool checked)
{
    if(checked)
        ui->cbInspecao->setChecked(false);
}

void MainWindow::on_cbInspecao_clicked(bool checked)
{
    if(checked)
        ui->cbFimOp->setChecked(false);
}

void MainWindow::on_cbFimOpJog_clicked(bool checked)
{
    if(checked)
        ui->cbInspecaoJog->setChecked(false);
}

void MainWindow::on_cbInspecaoJog_toggled(bool checked)
{
    if(checked)
        ui->cbFimOpJog->setChecked(false);
}
