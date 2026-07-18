ARG ROS_DISTRO=lyrical

# Base image
FROM osrf/ros:${ROS_DISTRO}-desktop
ENV ROS_DISTRO=${ROS_DISTRO}
SHELL [ "/bin/bash", "-c" ]
ARG HOST_UID=1000 # set default user ID

# Update system
RUN apt-get update \
    && apt-get upgrade -y

# Install utilities/packages
RUN apt-get install \
    ros-dev-tools \
    ros-${ROS_DISTRO}-plotjuggler \
    zsh \
    vim \
    -y

# Install dependencies and build
WORKDIR /rosflight_ws
COPY src tmp
RUN rosdep install --from-paths . --ignore-src -y \
    && rm -rf tmp

# Add default "ubuntu" user to needed groups
RUN if ! getent passwd ${HOST_UID}; then \
        useradd -u ${HOST_UID} -ms /usr/bin/zsh ubuntu; \
    fi \
    && usermod -aG sudo,dialout,plugdev ubuntu \
    && echo "ubuntu:pw" | chpasswd
USER ubuntu

# Setup ROS environment variables
RUN echo "source /rosflight_ws/install/setup.zsh" >> /home/ubuntu/.zshrc

# Add autocompletion for ROS commands with zsh
RUN echo 'eval "$(register-python-argcomplete ros2)"' >> /home/ubuntu/.zshrc \
    && echo 'eval "$(register-python-argcomplete colcon)"' >> /home/ubuntu/.zshrc

# Temporary fix for running ROS in Docker
RUN echo "ulimit -n 1024" >> /home/ubuntu/.zshrc

ENTRYPOINT [ "/usr/bin/zsh" ]

