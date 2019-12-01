#include "connectionprompt.h"
#include "ui_connectionprompt.h"

ConnectionPrompt::ConnectionPrompt(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::ConnectionPrompt)
{
    ui->setupUi(this);
    ui->ip1->setValidator(new QIntValidator(0, 255, this));
    ui->ip2->setValidator(new QIntValidator(0, 255, this));
    ui->ip3->setValidator(new QIntValidator(0, 255, this));
    ui->ip4->setValidator(new QIntValidator(0, 255, this));
    ui->port->setValidator(new QIntValidator(0, 65535, this));
    setWindowModality(Qt::WindowModality::ApplicationModal);
}

ConnectionPrompt::~ConnectionPrompt()
{
    delete ui;
}

void ConnectionPrompt::on_btSalvar_clicked()
{
    if(ui->ip1->text().toInt()>255 || ui->ip2->text().toInt()>255 || ui->ip3->text().toInt()>255
            || ui->ip4->text().toInt()>255 || ui->port->text().toInt() > 65535)
        return;
    QString ResultText = ui->ip1->text()+"."+ui->ip2->text()+"."+ui->ip3->text()+"."+ui->ip4->text();
    emit updateIP(ResultText);
    emit updatePort(ui->port->text().toInt());
    this->close();
}

void ConnectionPrompt::on_btFechar_clicked()
{
    this->close();
}
