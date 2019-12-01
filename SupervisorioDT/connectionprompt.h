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
    explicit ConnectionPrompt(QWidget *parent = nullptr);
    ~ConnectionPrompt();

private slots:
    void on_btSalvar_clicked();

    void on_btFechar_clicked();

signals:
    void updateIP(QString IP);
    void updatePort(int port);

private:
    Ui::ConnectionPrompt *ui;
};

#endif // CONNECTIONPROMPT_H
