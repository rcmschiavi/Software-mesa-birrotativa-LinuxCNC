#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    this->connectionWindow = new ConnectionPrompt(this, beagleBoneIP, beagleBonePort);
    this->tcpSocket = new QTcpSocket();

    //Conexão de sinais e slots entre a janela principal e a janela de configuração
    connect(this->connectionWindow, SIGNAL(updateIP(QString)), this, SLOT(saveIpConfiguration(QString)));
    connect(this->connectionWindow, SIGNAL(updatePort(int)), this, SLOT(savePortConfiguration(int)));
    connect(ui->actionAbrir_Programa, SIGNAL(triggered()), this, SLOT(openFileAct()));
    connect(ui->actionSalvar_Programa, SIGNAL(triggered()), this, SLOT(saveFileAct()));
    connect(ui->actionSobre, SIGNAL(triggered()),this,SLOT(aboutSupervisorio()));
}

MainWindow::~MainWindow()
{
    delete ui;
}

//=========================================CLOSE EVENT==============================================
void MainWindow::closeEvent(QCloseEvent *event)
{
    if (this->stateNow == STANDBY)
    {
        event->accept();
    }
    else
        event->ignore(); // Don't close.
}
//=========================================FILE MANAGEMENT==========================================

void MainWindow::saveJsonToFile(QJsonDocument doc)
{
    QString fileName = QFileDialog::getSaveFileName(this,tr("Salvar Programa"), "C:/", tr("JSON Files(*.json)"));
    if(fileName.isNull()) return;
    QFile jsonFile(fileName);
    jsonFile.open(QFile::WriteOnly);
    jsonFile.write(doc.toJson());
}

QJsonDocument MainWindow::loadJsonFromFile()
{
    QString fileName = QFileDialog::getOpenFileName(this,tr("Abrir Programa"), "C:/", tr("JSON Files(*.json)"));
    QJsonDocument doc;
    if(fileName.isNull()) return doc;
    QFile jsonFile(fileName);
    jsonFile.open(QFile::ReadOnly);
    return doc.fromJson(jsonFile.readAll());
}

void MainWindow::openFileAct()
{
    int ret = QMessageBox::warning(this,"Aviso!","Prosseguir irá apagar o programa atual!", QMessageBox::Ok|QMessageBox::Cancel);
    if(ret == QMessageBox::Ok)
    {
        QJsonDocument doc = loadJsonFromFile();
        if(doc.isEmpty())
        {
            ui->warningLog->append("Arquivo Inválido");
            return;
        }
        QJsonArray movement;
        double B_ang;
        double C_ang;
        double veloc;
        bool fim_op;
        bool inspect;
        QJsonArray arrayOfMovements = doc.object().value("params").toArray();
        clearWidgetTable();
        for(int i=0; i<arrayOfMovements.size(); i++)
        {
            try{
            movement = arrayOfMovements.at(i).toArray();
            B_ang = movement.at(0).toDouble();
            C_ang = movement.at(1).toDouble();
            veloc = movement.at(2).toDouble();
            fim_op = movement.at(3).toBool();
            inspect = movement.at(4).toBool();
            drawWidgetTable(B_ang,C_ang,veloc,fim_op,inspect);
            }
            catch(...)
            {
                ui->warningLog->append("Erro na leitura do arquivo, formato inesperado.");
                clearWidgetTable();
                return;
            }
        }
        ui->warningLog->append("Programa carregado com sucesso.");
    }
    else if(ret == QMessageBox::Cancel)
    {
        return;
    }
}

void MainWindow::saveFileAct()
{
    QJsonObject programaObj = loadWidgetTable();
    QJsonDocument doc;
    doc.setObject(programaObj);
    saveJsonToFile(doc);
    ui->warningLog->append("Programa salvo com sucesso.");
}

void MainWindow::aboutSupervisorio()
{
    QMessageBox::about(this,"Sobre",tr("Supervisório Dream Team\n\n""Interface desenvolvida para o controle de uma\n"
                                       "célula robótica constituída pelo robô FANUC e\n uma Mesa Bi-Rotativa com sistema de inspeção.\n\n"
                                       "Versão: 1.0"));
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
    //Estrutura de dados JsonDocument a ser enviado.
    QJsonDocument doc;
    //Preenche JsonObject no documento
    doc.setObject(obj);
    //Converte para json.
    QByteArray message = doc.toJson();
    //Envia o arquivo via TCP.
    if(tcpSocket->isOpen())
        tcpSocket->write(message);
    else
        ui->warningLog->append("Falha na conexão");
}

QJsonObject MainWindow::recieveJsonThroughSocket()
{
   QString rawData = QString(tcpSocket->readAll());
   QByteArray encodedData = rawData.toUtf8();
   QJsonDocument doc = QJsonDocument::fromJson(encodedData);
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
    recieverObject = recieveJsonThroughSocket();
    if(recieverObject.isEmpty())
        return;
    //Aqui serão inseridos os parsers para absorver os dados JSON recebidos pela GUI.
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
       tcpSocket->connectToHost(QHostAddress(beagleBoneIP), beagleBonePort);
       if(tcpSocket->waitForConnected(5000))
       {
           connect(this->tcpSocket, SIGNAL(readyRead()), this, SLOT(onReadyRead()));
           this->connectionState = true;
           this->stateNow = CONNECTED_STANDBY;
           ui->stateConnected->setText("SIM");
           changeWindowState(CONNECTED_STANDBY);

       }
       else
       {
           ui->warningLog->append("Conexão indisponível");
           ui->btConnect->setChecked(false);
           return;
       }

   }
   else
   {
       if(this->stateNow == CONNECTED_STANDBY)
       {
           tcpSocket->disconnectFromHost();
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
        if(this->stateNow == READY && this->homed)
        {
            changeWindowState(AUTO);
        }
        else
        {
            if(!this->homed)
                ui->warningLog->append("Favor fazer a rotina de home.");
            ui->btAuto->setChecked(false);
        }
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

void MainWindow::on_btHome_clicked(bool checked)
{
    if(checked)
    {
        //Só executa o homing durante JOG ou AUTO
        if(this->stateNow == JOG || this->stateNow == AUTO)
        {
            //Define o estado da BBB como homing (só volta a false quando a BBB retornar o status homing ok
            this->homing = true;
            QJsonObject senderObject{{"mode","home"},{"params",0}};
            sendJsonThroughSocket(senderObject);
        }
        else
            ui->btAuto->setChecked(false);
    }
    else
    {
        if(!((this->stateNow == JOG || this->stateNow == AUTO) && !this->homing && this->homed))
            ui->btAuto->setChecked(true);
    }
}

void MainWindow::on_btGO_clicked()
{
    if(this->stateNow == JOG && this->homed)
    {
        QJsonArray movement;
        movement.append(ui->sbBJog->value());
        movement.append(ui->sbCJog->value());
        movement.append(ui->sbVelocidadeJog->value());
        //FimOP e Inspect são sempre falsos no modo Jog.
        movement.append(0);
        movement.append(0);
        QJsonObject senderObject{{"mode","jog"},{"params",movement}};
        sendJsonThroughSocket(senderObject);
    }
    else if(this->stateNow == JOG && !this->homed)
    {
        ui->warningLog->append("Favor fazer a rotina de Home.");
    }
}

void MainWindow::on_btCycStart_clicked()
{
    if((this->stateNow == AUTO) && this->homed && this->programActive && !programExec && !taskExec)
    {
        this->stateNow = AUTO_RUN;
        changeWindowState(AUTO_RUN);
        QJsonObject senderObject{{"mode","cycStart"},{"params",0}};
        sendJsonThroughSocket(senderObject);
    }
    else
        ui->warningLog->append("Checar home, programa ativo e máquina parada.");
}


void MainWindow::on_btAtualizar_clicked()
{
    QJsonArray paramArray;
    paramArray.append(ui->dsbDBCP->value());
    paramArray.append(ui->dsbTol->value());
    //Se o valor de calibração for zero, não alterar o valor padrão.
    paramArray.append(0);
    QJsonObject senderObject{{"mode","inspection"},{"params",paramArray}};
    sendJsonThroughSocket(senderObject);
}

void MainWindow::on_btAlterar_clicked()
{
   int ret = QMessageBox::warning(this, tr("Aviso!"), tr("O valor de calibração só deve ser mudado\n"
                                                "se o sistema físico de inspeção for mudado!\n"
                                                "Aperte Salvar para continuar."), QMessageBox::Save|QMessageBox::Discard);

   if(ret == QMessageBox::Save)
   {
       QJsonArray paramArray;
       paramArray.append(ui->dsbDBCP->value());
       paramArray.append(ui->dsbTol->value());
       paramArray.append(ui->sbCalib->value());
       QJsonObject senderObject{{"mode","inspection"},{"params", paramArray}};
   }
   else if(ret == QMessageBox::Discard)
       return;
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

//=============================================PROGRAM EDITOR===============================

void MainWindow::drawWidgetTable(double B_ang, double C_ang, double veloc, bool fim_op, bool inspect)
{
    int auxPointer = editorLinePointer;
    if(clearOcurred)
    {
        editorLinePointer = ui->programEditor->currentRow();
        this->clearOcurred=false;
    }
    else
        editorLinePointer = ui->programEditor->currentRow()+1;
    ui->programEditor->insertRow(editorLinePointer);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(editorLinePointer));
    ui->programEditor->setItem(editorLinePointer,TASK,cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(B_ang));
    ui->programEditor->setItem(editorLinePointer,B_ANG,cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(C_ang));
    ui->programEditor->setItem(editorLinePointer,C_ANG,cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText(QString::number(veloc));
    ui->programEditor->setItem(editorLinePointer,VELOC,cellPtr);
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

void MainWindow::clearWidgetTable()
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
    cellPtr->setText("VELOC.");
    ui->programEditor->setHorizontalHeaderItem(VELOC, cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText("FIM OP?");
    ui->programEditor->setHorizontalHeaderItem(FIM_OP, cellPtr);
    cellPtr = new QTableWidgetItem;
    cellPtr->setText("INSPECT?");
    ui->programEditor->setHorizontalHeaderItem(INSPECT, cellPtr);
    ui->programEditor->setCurrentCell(0,0);
    this->clearOcurred = true;
    drawWidgetTable(0,0,1,false,false);
    ui->programEditor->setRowCount(1);
}

void MainWindow::on_btAddTarefa_clicked()
{
    double B_Value;
    double C_Value;
    double veloc;
    bool fim_op;
    bool inspect;
    if(this->stateNow == PROG)
    {
        B_Value = ui->sbBProg->value();
        C_Value = ui->sbCProg->value();
        veloc = ui->sbVelocidade->value();
        fim_op = ui->cbFimOp->isChecked();
        inspect = ui->cbInspecao->isChecked();
    }
    else if(this->stateNow == JOG && ui->cbTeach->isChecked())
    {
        B_Value = ui->sbBJog->value();
        C_Value = ui->sbCJog->value();
        veloc = ui->sbVelocidadeJog->value();
        fim_op = ui->cbFimOpJog->isChecked();
        inspect = ui->cbInspecaoJog->isChecked();
    }
    else
        return;
    drawWidgetTable(B_Value,C_Value,veloc,fim_op,inspect);
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
        clearWidgetTable();
    }
}

QJsonObject MainWindow::loadWidgetTable()
{
    QJsonArray arrayOfMovements;
    ui->warningLog->append("Loading Data...");
    //Varrendo todas as linhas
    for(int i=0; i<ui->programEditor->rowCount(); i++)
    {
        //Varrendo todas as colunas exceto Task #
        QJsonArray movement;
        for(int j=1; j<ui->programEditor->columnCount(); j++)
        {
            if(ui->programEditor->item(i,j)->text().toLower() == "true")
                movement.append(1);
            else if(ui->programEditor->item(i,j)->text().toLower() == "false")
                movement.append(0);
            else
                movement.append(ui->programEditor->item(i,j)->text().toDouble());
        }
        arrayOfMovements.append(movement);
    }
    QJsonObject senderObject{
        {"mode","program"},
        {"params",arrayOfMovements}
    };
    return senderObject;
}

void MainWindow::on_btCarregar_clicked()
{
    if(this->stateNow == PROG)
    {
        //O programa não é nulo
        if(ui->programEditor->rowCount() >= 1)
        {
            QJsonObject senderObject = loadWidgetTable();
            sendJsonThroughSocket(senderObject);
        }
        else
            ui->warningLog->append("O programa está vazio.");
    }
}

//Mocks (debug)

void MainWindow::on_homeMck_clicked()
{
    this->homed = true;
    this->homing = false;
}

void MainWindow::on_activePrgMck_clicked()
{
    this->programActive = true;
}
