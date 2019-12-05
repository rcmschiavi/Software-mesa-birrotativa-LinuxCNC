#ifndef CONNECTIONPROMPT_H
#define CONNECTIONPROMPT_H

#include <QDialog>
#include <QValidator>

namespace Ui {
class ConnectionPrompt;
}

class ConnectionPrompt : public QDialog
{
    Q_OBJECT

public:
    explicit ConnectionPrompt(QWidget *parent = nullptr, QString oldip="127.0.0.1", int oldport=10000);
    ~ConnectionPrompt();

private slots:
    void on_btSalvar_clicked();

    void on_btFechar_clicked();

signals:
    void updateIP(QString IP);
    void updatePort(int port);

private:
    Ui::ConnectionPrompt *ui;
    QString lastip;
    int lastport;
};

#endif // CONNECTIONPROMPT_H
