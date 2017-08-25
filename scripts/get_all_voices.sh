# mycroft alan pope

wget -c https://github.com/MycroftAI/mimic/raw/master/voices/mycroft_voice_4.0.flitevox

# cmu

wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_rms.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_jmk.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_bdl.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_aew.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_slt.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_clb.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_ljm.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_eey.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_awb.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_ahw.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_fem.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_rxr.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_aup.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_gka.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_ksp.flitevox
wget -c http://www.festvox.org/flite/packed/flite-2.0/voices/cmu_us_axb.flitevox

# cmu artic

wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_awb_arctic-0.90-release.tar.bz2
wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_bdl_arctic-0.95-release.tar.bz2
wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_clb_arctic-0.95-release.tar.bz2
wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_jmk_arctic-0.95-release.tar.bz2
wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_rms_arctic-0.95-release.tar.bz2
wget -c http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_slt_arctic-0.95-release.tar.bz2

tar xf cmu_us_awb_arctic-0.90-release.tar.bz2
tar xf cmu_us_bdl_arctic-0.95-release.tar.bz2
tar xf cmu_us_clb_arctic-0.95-release.tar.bz2
tar xf cmu_us_jmk_arctic-0.95-release.tar.bz2
tar xf cmu_us_rms_arctic-0.95-release.tar.bz2
tar xf cmu_us_slt_arctic-0.95-release.tar.bz2

# mbrola voices

# wget http://tcts.fpms.ac.be/synthesis/mbrola/bin/pclinux/mbrola3.0.1h_i386.deb
# sudo dpkg -i mbrola3.0.1h_i386.deb
wget -c http://tcts.fpms.ac.be/synthesis/mbrola/dba/us1/us1-980512.zip
wget -c http://tcts.fpms.ac.be/synthesis/mbrola/dba/us2/us2-980812.zip
wget -c http://tcts.fpms.ac.be/synthesis/mbrola/dba/us3/us3-990208.zip
wget -c http://www.festvox.org/packed/festival/latest/festvox_us1.tar.gz
wget -c http://www.festvox.org/packed/festival/latest/festvox_us2.tar.gz
wget -c http://www.festvox.org/packed/festival/latest/festvox_us3.tar.gz

unzip -x us1-980512.zip
unzip -x us2-980812.zip
unzip -x us3-990208.zip
tar xvf festvox_us1.tar.gz
tar xvf festvox_us2.tar.gz
tar xvf festvox_us3.tar.gz

# enhanced Nitech HTS voices

wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_awb_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_bdl_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_clb_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_rms_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_slt_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/2.1/festvox_nitech_us_jmk_arctic_hts-2.1.tar.bz2
wget -c http://hts.sp.nitech.ac.jp/archives/1.1.1/cmu_us_kal_com_hts.tar.gz
wget -c http://hts.sp.nitech.ac.jp/archives/1.1.1/cstr_us_ked_timit_hts.tar.gz

tar xvf festvox_nitech_us_awb_arctic_hts-2.1.tar.bz2
tar xvf festvox_nitech_us_bdl_arctic_hts-2.1.tar.bz2
tar xvf festvox_nitech_us_clb_arctic_hts-2.1.tar.bz2
tar xvf festvox_nitech_us_rms_arctic_hts-2.1.tar.bz2
tar xvf festvox_nitech_us_slt_arctic_hts-2.1.tar.bz2
tar xvf festvox_nitech_us_jmk_arctic_hts-2.1.tar.bz2
tar xvf cmu_us_kal_com_hts.tar.gz
tar xvf cstr_us_ked_timit_hts.tar.gz