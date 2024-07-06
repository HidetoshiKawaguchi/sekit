FROM ubuntu:24.04

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo

# SSHサーバーの設定
RUN mkdir /var/run/sshd

# 公開鍵認証の設定
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
COPY id_rsa.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# sudoersの設定
RUN echo "root ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ポート22を開放
EXPOSE 22

# SSHサーバーをデーモンとして実行
CMD ["/usr/sbin/sshd", "-D"]
