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

    //Definição das velocidades máximas
    ui->sbVelocidade->setMaximum(this->C_maxSpeed);
    ui->sbVelocidadeJog->setMaximum(this->C_maxSpeed);
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
    {
        ui->warningLog->append("Favor desconectar o sistema com segurança antes de fechar.");
        event->ignore(); // Don't close.
    }
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

void MainWindow::recieveJsonProgramFromBBB(QJsonObject program)
{
    int ret = QMessageBox::warning(this,"Aviso!","Prosseguir irá apagar o programa atual!", QMessageBox::Ok|QMessageBox::Cancel);
    if(ret == QMessageBox::Ok)
    {
        QJsonArray movement;
        double B_ang;
        double C_ang;
        double veloc;
        bool fim_op;
        bool inspect;
        QJsonArray arrayOfMovements = program.value("params").toArray();
        clearWidgetTable();
        for(int i=0; i<arrayOfMovements.size(); i++)
        {
            try{
                movement = arrayOfMovements.at(i).toArray();
                B_ang = movement.at(0).toDouble();
                C_ang = movement.at(1).toDouble();
                veloc = movement.at(2).toDouble();
                fim_op = movement.at(3).toInt();
                inspect = movement.at(4).toInt();
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

//==============================================SUPORTE E USER=====================================
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

QJsonDocument MainWindow::recieveJsonThroughSocket()
{
   QString rawData = QString(tcpSocket->readAll());
   QByteArray encodedData = rawData.toUtf8();
   QJsonDocument doc = QJsonDocument::fromJson(encodedData);
   return doc;
}

void MainWindow::on_btConfig_clicked()
{
    this->connectionWindow->show();
}

//Slot acionado sempre que exite um pacote TCP pronto para leitura.
void MainWindow::onReadyRead()
{
    if(!recievingImage)
    {
        QJsonDocument recieverDocument = recieveJsonThroughSocket();
        QJsonObject obj = recieverDocument.object();
        QString keyValue = obj.value("mode").toString();
        if(keyValue == "EXTESTOP")
        {
            //Adicionar testes de valor, para reiniciar a máquina de estados do supervisório
            bool tipo = obj.value("params").toInt();
            if(tipo == true)
            {
                ui->warningLog->append("A parada de emergência externa foi acionada, favor checar integridade da célula");
                changeWindowState(EXTESTOP);
            }
            else
            {
                changeWindowState(CONNECTED_STANDBY);
                homed = false;
                homing = false;
                turnedOn = false;
                programActive = false;
                programExec = false;
                taskExec = false;
                inspection = false;
                changeWindowStatus();
            }
        }
        else if(keyValue == "STATUS")
        {
            QJsonArray arr = obj.value("params").toArray();
            homed = arr.at(0).toInt();
            homing = arr.at(1).toInt();
            turnedOn = arr.at(2).toInt();
            programActive = arr.at(3).toInt();
            programExec = arr.at(4).toInt();
            taskExec = arr.at(5).toInt();
            inspection = arr.at(6).toInt();
            changeWindowStatus();
        }
        else if(keyValue == "INSPECTION")
        {
            int param = obj.value("params").toInt();
            if(param == 1)
            {
                ui->warningLog->append("Calibração terminada");
            }
            if(param == -1)
            {
                ui->warningLog->append("Erro de calibração");
            }
        }
        else if(keyValue == "PROGRAM")
        {
            if(this->stateNow == PROG)
            {
                ui->warningLog->append("Programa Recebido");
                recieveJsonProgramFromBBB(obj);
            }
            else
                ui->warningLog->append("O programa foi recebido, mas a interface deve estar em modo programa. Tente Novamente.");
        }
        else if(keyValue == "FRAME")
        {
            ui->warningLog->append("Frame chegou");
            this->frameBufferSize = obj.value("params").toInt();
            ui->warningLog->append(QString::number(frameBufferSize));
            this->recievingImage = true;
        }
    }
    else
    {
        this->dataBuffer = tcpSocket->read(frameBufferSize);
        ui->cameraImage->clear();
        QBuffer buffer(&dataBuffer);
        buffer.open(QIODevice::ReadOnly);
        QImageReader reader(&buffer, "jpg");
        QImage image = reader.read();
        if(image.isNull())
        {
            ui->warningLog->append("Imagem invalida");
        }
        else
            ui->cameraImage->setPixmap(QPixmap::fromImage(image));
        recievingImage = false;
        buffer.close();
        this->dataBuffer.clear();
    }
}

//=============================================STATE MACHINE===============================
void MainWindow::changeWindowStatus()
{
    if(homed)
        ui->stateHomed->setText("SIM");
    else
        ui->stateHomed->setText("NÃO");
    if(turnedOn)
        ui->stateTurnedOn->setText("SIM");
    else
        ui->stateTurnedOn->setText("NÃO");
    if(programActive)
        ui->stateProgramActive->setText("SIM");
    else
        ui->stateProgramActive->setText("NÃO");
    if(programExec)
        ui->stateProgramExec->setText("SIM");
    else
        ui->stateProgramExec->setText("NÃO");
    if(taskExec)
        ui->stateTaskExec->setText("SIM");
    else
        ui->stateTaskExec->setText("NÃO");
    if(inspection)
        ui->stateInspection->setText("SIM");
    else
        ui->stateInspection->setText("NÃO");
}


void MainWindow::changeWindowState(int state)
{
    QJsonObject senderObject;
    //Função que prepara a máquina de estados da janela.
    switch(state)
    {
    case EXTESTOP:
        senderObject = {{"mode","EXTESTOP"},{"params",1}};
        sendJsonThroughSocket(senderObject);
        ui->btEstop->setEnabled(false);
        ui->btLiga->setEnabled(false);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(false);
        ui->groupInspect->setEnabled(false);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->cameraImage->setEnabled(false);
        this->stateNow = EXTESTOP;
        ui->stateEstado->setText("EXTESTOP");
        break;
    case ESTOP:
        senderObject = {{"mode","ESTOP"},{"params",0}};
        sendJsonThroughSocket(senderObject);
        ui->btEstop->setEnabled(true);
        ui->btLiga->setEnabled(true);
        ui->btHome->setEnabled(false);
        ui->groupJog->setEnabled(false);
        ui->groupProg->setEnabled(false);
        ui->groupOpMode->setEnabled(true);
        ui->groupInspect->setEnabled(false);
        ui->groupStatus->setEnabled(true);
        ui->groupEditor->setEnabled(false);
        ui->groupProgCtrl->setEnabled(false);
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
        ui->btExtEstop->setEnabled(false);
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
        ui->groupProgCtrl->setEnabled(false);
        ui->cameraImage->setEnabled(true);
        ui->btExtEstop->setEnabled(true);
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
        ui->groupProgCtrl->setEnabled(true);
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
       this->connectionState = true;
       this->stateNow = CONNECTED_STANDBY;
       ui->stateConnected->setText("SIM");
       changeWindowState(CONNECTED_STANDBY);

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

void MainWindow::on_btExtEstop_clicked()
{
    changeWindowState(EXTESTOP);
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
        if((this->stateNow == JOG || this->stateNow == AUTO) && !this->taskExec && !this->programExec && !this->homing)
        {
            //Define o estado da BBB como homing (só volta a false quando a BBB retornar o status homing ok
            QJsonObject senderObject{{"mode","HOME"},{"params",0}};
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
    if(this->stateNow == JOG && this->homed && !this->taskExec && !this->programExec)
    {
        QJsonArray movement;
        movement.append(ui->sbBJog->value());
        movement.append(ui->sbCJog->value());
        movement.append(ui->sbVelocidadeJog->value());
        QJsonObject senderObject{{"mode","JOG"},{"params",movement}};
        sendJsonThroughSocket(senderObject);
    }
    else
    {
        if(this->programExec)
            ui->warningLog->append("Programa em Execução");
        if(this->taskExec)
            ui->warningLog->append("Aguarde a execução da tarefa");
        if(!this->homed)
            ui->warningLog->append("Favor fazer a rotina de Home.");
    }
}

void MainWindow::on_btCycStart_clicked()
{
    if((this->stateNow == AUTO) && this->homed && this->programActive && !programExec && !taskExec)
    {
        this->stateNow = AUTO_RUN;
        changeWindowState(AUTO_RUN);
        QJsonObject senderObject{{"mode","CYCSTART"},{"params",0}};
        sendJsonThroughSocket(senderObject);
    }
    else
    {
        if(!this->programActive)
            ui->warningLog->append("Não há programa ativo");
        if(this->programExec)
            ui->warningLog->append("Programa em Execução");
        if(this->taskExec)
            ui->warningLog->append("Aguarde a execução da tarefa");
        if(!this->homed)
            ui->warningLog->append("Favor fazer a rotina de Home.");
    }
}


void MainWindow::on_btAtualizar_clicked()
{
    QJsonArray paramArray;
    paramArray.append(ui->dsbDBCP->value());
    paramArray.append(ui->dsbTol->value());
    //Valor 0 significa que não há mudança no padrão de calibração.
    paramArray.append(0);
    QJsonObject senderObject{{"mode","INSPECTION"},{"params",paramArray}};
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
       QJsonObject senderObject{{"mode","INSPECTION"},{"params", paramArray}};
   }
   else if(ret == QMessageBox::Discard)
       return;
}

//==========================================CheckBox Handlers=========================

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


void MainWindow::on_cbLinear_clicked(bool checked)
{
    if(checked)
        ui->cbJunta->setChecked(false);
    else
        ui->cbJunta->setChecked(true);
}


void MainWindow::on_cbJunta_clicked(bool checked)
{
    if(checked)
        ui->cbLinear->setChecked(false);
    else
        ui->cbLinear->setChecked(true);
}

void MainWindow::on_cbLinearJog_clicked(bool checked)
{
    if(checked)
        ui->cbJuntaJog->setChecked(false);
    else
        ui->cbJuntaJog->setChecked(true);
}

void MainWindow::on_cbJuntaJog_clicked(bool checked)
{
    if(checked)
        ui->cbLinearJog->setChecked(false);
    else
        ui->cbLinearJog->setChecked(true);
}

//=============================================PROGRAM CONTROL==============================

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

void MainWindow::on_btReceber_clicked()
{
    if(this->stateNow == PROG && this->programActive)
    {
        ui->warningLog->append("Requisitando Dados...");
        QJsonObject senderObject{
            {"mode","PROGRAM"},
            {"operation", 1},
            {"params",0}
        };
        sendJsonThroughSocket(senderObject);
    }
}

void MainWindow::on_btDeletar_clicked()
{
    if(this->stateNow == PROG && this->programActive)
    {
        ui->warningLog->append("Deletando Programa...");
        QJsonObject senderObject{
            {"mode","PROGRAM"},
            {"operation", -1},
            {"params",0}
        };
        sendJsonThroughSocket(senderObject);
    }
    else if(!this->programActive)
    {
        ui->warningLog->append("Não há programa ativo.");
    }
}

//=============================================FUNÇÕES PARA CINEMATICA======================

double MainWindow::checkSpeeds(double B_ang, double C_ang, double veloc)
{
    this->B_lastPos=ui->programEditor->item(ui->programEditor->currentRow(),B_ANG)->text().toDouble();
    this->C_lastPos=ui->programEditor->item(ui->programEditor->currentRow(),C_ANG)->text().toDouble();
    double t_b = qAbs(B_ang - B_lastPos)/veloc;
    double t_c = qAbs(C_ang - C_lastPos)/veloc;
    if(t_b<=0 && t_c<=0)
    {
        ui->warningLog->append("Não há movimento, a velocidade é nula.");
        return 0;
    }
    //Se não há deslocamento em B e há deslocamento em C testa a velocidade de C.
    else if(t_b <= 0 && t_c >= 0)
    {
        if(veloc <= this->C_maxSpeed)
            return veloc;
        else
        {
            ui->warningLog->append("A velocidade desejada excede o limite do eixo. A velocidade máxima foi definida por padrão.");
            return C_maxSpeed;
        }
    }
    //Se não há deslocamento em C e há Deslocamento em B testa a velocidade em B
    else if(t_c <= 0 && t_b >= 0)
    {
        if(veloc <= this->B_maxSpeed)
            return veloc;
        else
        {
            ui->warningLog->append("A velocidade desejada excede o limite do eixo. A velocidade máxima foi definida por padrão.");
            return B_maxSpeed;
        }
    }
    else
    {
        double largestTime = 0;
        if(t_b >= t_c)
            largestTime = t_b;
        else
            largestTime = t_c;
        double actualSpeed_B = qAbs(B_ang - B_lastPos)/largestTime;
        double actualSpeed_C = qAbs(C_ang - C_lastPos)/largestTime;
        if(actualSpeed_B > B_maxSpeed && actualSpeed_C <= C_maxSpeed)
        {
            ui->warningLog->append("O movimento não pode ser linear, o eixo B se move acima da velocidade máxima");
            ui->warningLog->append("Velocidade:" + QString::number(actualSpeed_B) + "graus/s");
            return 0;
        }
        else if(actualSpeed_C > C_maxSpeed && actualSpeed_B <= B_maxSpeed)
        {
            ui->warningLog->append("O movimento não pode ser linear, o eixo C se move acima da velocidade máxima");
            ui->warningLog->append("Velocidade:" + QString::number(actualSpeed_C) + "graus/s");
            return 0;
        }
        else if(actualSpeed_B > B_maxSpeed && actualSpeed_C > C_maxSpeed)
        {
            ui->warningLog->append("O movimento não pode ser linear, os eixos B e C se movem acima das velocidades máximas");
            ui->warningLog->append("Velocidade:" + QString::number(actualSpeed_B) + "graus/s");
            ui->warningLog->append("Velocidade:" + QString::number(actualSpeed_C) + "graus/s");
            return 0;
        }
    }
    return veloc;
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
    double resultSpeed;
    if(this->stateNow == PROG)
    {
        B_Value = ui->sbBProg->value();
        C_Value = ui->sbCProg->value();
        veloc = ui->sbVelocidade->value();
        fim_op = ui->cbFimOp->isChecked();
        inspect = ui->cbInspecao->isChecked();
        if(ui->cbLinear->isChecked())
            resultSpeed = checkSpeeds(B_Value,C_Value,veloc);
        else
            resultSpeed = veloc;
    }
    else if(this->stateNow == JOG && ui->cbTeach->isChecked())
    {
        B_Value = ui->sbBJog->value();
        C_Value = ui->sbCJog->value();
        veloc = ui->sbVelocidadeJog->value();
        fim_op = ui->cbFimOpJog->isChecked();
        inspect = ui->cbInspecaoJog->isChecked();
        if(ui->cbLinearJog->isChecked())
            resultSpeed = checkSpeeds(B_Value,C_Value,veloc);
        else
            resultSpeed = veloc;
    }
    else
        return;
    if(resultSpeed <= 0)
    {
        ui->warningLog->append("Movimento inválido.");
        return;
    }
    else
        drawWidgetTable(B_Value,C_Value,resultSpeed,fim_op,inspect);
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
        {"mode","PROGRAM"},
        {"params",arrayOfMovements}
    };
    return senderObject;
}

