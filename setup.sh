function install_requirements() {
    pip3 install ansi==0.3.6;
    pip3 install git+https://github.com/jose/javalang.git@start_position_and_end_position;
    pip3 install matplotlib==3.3.4;
    pip3 install nltk==3.6.7
    pip3 install numpy==1.21.6
    pip3 install seaborn==0.12.2
    pip3 install torch==1.12.1
    pip3 install transformers==4.22.2
    pip3 install wordninja==2.0.0
}

function download_projects() {
    mkdir -p projects;
    main=`pwd`;

    git clone https://github.com/apache/commons-cli projects/commons-cli;
    cd projects/commons-cli;
    git reset --hard b18139a6d1a48bdc19239454c8271ded8184c68a;
    cd $main;

    git clone https://github.com/jfree/jfreechart projects/jfreechart;
    cd projects/jfreechart;
    git reset --hard e2d6788d594c51941ddae337ae666fda5c52ad9f;
    cd $main;

    git clone https://github.com/apache/commons-codec projects/commons-codec;
    cd projects/commons-codec;
    git reset --hard 2eddb17292ea79a6734bc9b0c447ac6d9da0af53;
    cd $main;

    git clone https://github.com/apache/commons-collections projects/commons-collections;
    cd projects/commons-collections;
    git reset --hard 1f297c969c774a97bf72bc710c5e1e8a3e039f79;
    cd $main;

    git clone https://github.com/apache/commons-compress projects/commons-compress;
    cd projects/commons-compress;
    git reset --hard e6930d06cfebbdbee586b863481779b2c4b9b202;
    cd $main;

    git clone https://github.com/apache/commons-csv projects/commons-csv;
    cd projects/commons-csv;
    git reset --hard 420cd15cac9be508930570cb48eee63e25ad5d78;
    cd $main;

    git clone https://github.com/google/gson projects/gson;
    cd projects/gson;
    git reset --hard 19f54ee6ed33b7517c729c801bc57c8c0478be7d;
    cd $main;

    git clone https://github.com/apache/commons-lang projects/commons-lang;
    cd projects/commons-lang;
    git reset --hard eaff7e0a693455081932b53688029f0700447305;
    cd $main;

    git clone https://github.com/apache/commons-math projects/commons-math;
    cd projects/commons-math;
    git reset --hard 889d27b5d7b23eaf1ee984e93b892b5128afc454;
    cd $main;

    git clone https://github.com/apache/commons-jxpath projects/commons-jxpath;
    cd projects/commons-jxpath;
    git reset --hard db457cfd3a0cb45a61030ab2d728e080035baef6;
    cd $main;

    git clone https://github.com/FasterXML/jackson-dataformat-xml projects/jackson-dataformat-xml;
    cd projects/jackson-dataformat-xml;
    git reset --hard 0e59be67bd3e9cfcd73b2b62a95bcc0f5b2dda3c;
    cd $main;

    git clone https://github.com/FasterXML/jackson-core projects/jackson-core;
    cd projects/jackson-core;
    git reset --hard 5956b59a77f9599317c7ca7eaa073cb5d5348940;
    cd $main;

    git clone https://github.com/FasterXML/jackson-databind projects/jackson-databind;
    cd projects/jackson-databind;
    git reset --hard 1c3c3d87380f7c7a961e169f3bd6bfeb877b89a6;
    cd $main;

    git clone https://github.com/jhy/jsoup projects/jsoup;
    cd projects/jsoup;
    git reset --hard e52224fbfe6632248cc58c593efae9a22ba2e622;
    cd $main;

    git clone https://github.com/JodaOrg/joda-time projects/joda-time;
    cd projects/joda-time;
    git reset --hard 0440038eabedcebc96dded95d836e0e1d576ee25;
    cd $main;
}

function build_projects {
    main=`pwd`;

    cd projects/commons-cli;
    mvn test --log-file build.log;
    cd $main;

    cd projects/jfreechart;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-codec;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-collections;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-compress;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-csv;
    mvn test --log-file build.log;
    cd $main;

    cd projects/gson;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-lang;
    JAVA_HOME=`/usr/libexec/java_home -v 1.8` mvn test --log-file build.log;
    cd $main;

    cd projects/commons-math;
    mvn test --log-file build.log;
    cd $main;

    cd projects/commons-jxpath;
    mvn test --log-file build.log;
    cd $main;

    cd projects/jackson-dataformat-xml;
    mvn test --log-file build.log;
    cd $main;

    cd projects/jackson-core;
    mvn test --log-file build.log;
    cd $main;

    cd projects/jackson-databind;
    mvn test --log-file build.log;
    cd $main;

    cd projects/jsoup;
    mvn test --log-file build.log;
    cd $main;

    cd projects/joda-time;
    JAVA_HOME=`/usr/libexec/java_home -v 1.8` mvn test --log-file build.log;
    cd $main;
}

install_requirements;
download_projects;
build_projects;
