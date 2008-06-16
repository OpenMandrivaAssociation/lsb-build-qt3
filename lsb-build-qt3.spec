# had to bump from 3.3.5 - wouldn't build with our gcc
%define qtver	 3.3.6
%define lsbbuild lsb-build-base

Summary: 	LSB Build environment qt3 package
Name: 		lsb-build-qt3
Version: 	3.1.1
Release: 	%mkrel 5
License: 	GPL
Group: 		Development/C++
Source: 	ftp://ftp.freestandards.org/pub/lsb/lsbdev/released-3.1.0/source/lsb-build-qt3-%{version}.tar.bz2
Source1: 	ftp://ftp.trolltech.com/qt/source/qt-x11-free-%qtver.tar.bz2
Patch0:		lsb-build-qt3-3.1.1-mandriva.patch
URL:            http://www.linuxbase.org/build
BuildRoot: 	%_tmppath/%name-%version-%release-root

%description
This package provides LSB qt3 building support for the
lsb-build packages.  It adds LSB qt headers.

%package        -n %{name}-devel
Summary:        LSB Build environment qt headers
Group:          Development/C++
Requires: 	lsb-build-base lsb-build-desktop-devel 
Requires:	lsb-build-cc lsb-build-c++-devel
Provides:	lsb-build-qt3
Obsoletes:	lsb-build-qt3
Conflicts:	qt3-devel
Conflicts:	%{_lib}qt3-devel

%description -n %{name}-devel
This package provides LSB qt building support for the
lsb-build packages.  It adds LSB qt headers.

%prep
%setup -q
%patch0 -p1 -b .mandriva
tar xjf %{SOURCE1}
# (sb) 64bit needs a different QTDIR and qmake.conf
%ifarch sparc64 ppc64 x86_64
sed -i 's|spec /usr/lib/lsb-build|spec /usr/lib64/lsb-build|' qmake
sed -i 's|QTDIR)/lib|QTDIR)/lib64|' linux-lsb-qt3/qmake.conf
%endif

# copy the linux-lsb-qt3 makespec needed for bootstrapping
cp -rpf linux-lsb-qt3 qt-x11-free-%qtver/mkspecs

# (sb) broken shell scripts in tarball
sed -i 's|#/bin/sh|#!/bin/sh|g' qmake uic moc

%build
export LSB_PRODUCT=desktop
cd qt-x11-free-%qtver
echo yes | ./configure -prefix %{_prefix} -headerdir %{_includedir}/%{lsbbuild}/qt3 -libdir %{_libdir}/%{lsbbuild}/qt3 -shared -release -thread 
#-platform linux-lsb-qt3 /* this would make it an lsb binary - necessary? */

IMAGE=$(pwd)/image
if [ ! -e "src/Makefile" ]; then
    echo "No such file: src/Makefile"
    exit 1
fi
# strip all dependencies from the install_headers target
# so that we don't have to build Qt itself to install all headers
sed -e 's/^install_headers:.*/install_headers:/' src/Makefile | sed -e 's/^install_headers_p:.*/install_headers_p:/' >src/Makefile.lsb

# build the build tools
make sub-src
make -C src/moc 
make -C tools/designer/uic 

%install
rm -rf $RPM_BUILD_ROOT

cd qt-x11-free-%qtver

make -C src -f Makefile.lsb install_headers INSTALL_ROOT=$RPM_BUILD_ROOT
make -C src -f Makefile.lsb install_headers_p INSTALL_ROOT=$RPM_BUILD_ROOT

# copy the tools
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp bin/qmake $RPM_BUILD_ROOT%{_bindir}/qmake_lsb_qt3
cp bin/moc $RPM_BUILD_ROOT%{_bindir}/moc_lsb_qt3
cp bin/uic $RPM_BUILD_ROOT%{_bindir}/uic_lsb_qt3

cd ..
cp uic qmake moc $RPM_BUILD_ROOT%{_bindir}

#copy linux-lsb mkspecs
mkdir -p $RPM_BUILD_ROOT%{_libdir}/%{lsbbuild}/qt3/mkspecs
cp -rpf linux-lsb-qt3/ $RPM_BUILD_ROOT%{_libdir}/%{lsbbuild}/qt3/mkspecs

%clean
rm -rf $RPM_BUILD_ROOT

%files -n %{name}-devel
%defattr(-,root,root)
%doc README Licence GPL
%{_bindir}/qmake*
%{_bindir}/moc*
%{_bindir}/uic*
%{_includedir}/%{lsbbuild}/qt3/*
%{_libdir}/%{lsbbuild}/qt3/mkspecs/*

