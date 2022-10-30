CREATE TABLE users(
    usr_cod         INTEGER PRIMARY KEY AUTOINCREMENT,
    usr_name        TEXT NOT NULL,
    usr_username    TEXT NOT NULL,
    usr_password    TEXT NOT NULL,
    usr_email       TEXT NOT NULL,
    usr_is_adm      INTEGER DEFAULT 0
);

CREATE TABLE patients(
    pat_cod     INTEGER PRIMARY KEY AUTOINCREMENT,
    pat_name    TEXT,
    pat_sex     TEXT,
    pat_birth   TEXT,
    pat_height  INTEGER,
    pat_weight  REAL,
    pat_imc     REAL
);

CREATE TABLE static_exams(
    sta_ex_cod  INTEGER PRIMARY KEY AUTOINCREMENT,
    sta_ex_aps  TEXT,
    sta_ex_mls  TEXT,
    sta_ex_date TEXT,
    sta_ex_type TEXT,
    usr_cod INTEGER,
    pat_cod INTEGER,
    FOREIGN KEY(usr_cod) REFERENCES users(usr_cod),
    FOREIGN KEY(pat_cod) REFERENCES patients(pat_cod)
);

CREATE TABLE dynamic_exams(
    dyn_ex_cod  INTEGER PRIMARY KEY AUTOINCREMENT,
    dyn_ex_cop_x  TEXT,
    dyn_ex_cop_y  TEXT,
    dyn_ex_date TEXT,
    usr_cod INTEGER,
    pat_cod INTEGER,
    FOREIGN KEY(usr_cod) REFERENCES users(usr_cod),
    FOREIGN KEY(pat_cod) REFERENCES patients(pat_cod)
);

CREATE TABLE devices(
    dev_cod         INTEGER PRIMARY KEY AUTOINCREMENT,
    dev_name        TEXT,
    dev_mac         TEXT,
    dev_is_default  INTEGER DEFAULT 0
);

CREATE TABLE calibrations(
    cal_cod             INTEGER PRIMARY KEY AUTOINCREMENT,
    cal_right_top       TEXT,
    cal_right_bottom    TEXT,
    cal_left_top        TEXT,
    cal_left_bottom     TEXT,
    cal_date            TEXT,
    dev_cod             INTEGER,
    FOREIGN KEY(dev_cod) REFERENCES devices(dev_cod)
);
