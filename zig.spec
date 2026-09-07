%bcond_with	bootstrap	# build with the precompiled compiler from upstream

%define	gitref	ab30a0b9a
%define	snap	20260905
%define	zigver	0.17.0-dev.2018+%{gitref}

%define	prebuilt_dir	%{name}-x86_64-linux-%{zigver}
#
Summary:	Programming language for maintaining robust, optimal and reusable software
Summary(pl.UTF-8):	Język programowania do tworzenia niezawodnego, optymalnego oprogramowania wielokrotnego użytku
Name:		zig
Version:	0.17.0
Release:	0.%{snap}.1
License:	MIT (compiler), MIT/BSD/LGPL v2.1+ and others (bundled libc sources)
Group:		Development/Languages
Source0:	https://ziglang.org/builds/%{name}-%{zigver}.tar.xz
# Source0-md5:	f44255f821df694f0cb32946f3878076
Source1:	https://ziglang.org/builds/%{name}-x86_64-linux-%{zigver}.tar.xz
# Source1-md5:	b3b96a6d9f38474651c228ef7c1a0ae4
URL:		https://ziglang.org/
# cmake/Findllvm.cmake accepts one LLVM major only and errors out on anything
# else, so this tracks whichever zig snapshot matches the LLVM PLD ships.
BuildRequires:	clang-devel >= 22.0.0
BuildRequires:	cmake >= 3.15
BuildRequires:	libstdc++-devel
BuildRequires:	lld-devel >= 22.0.0
BuildRequires:	llvm-devel >= 22.0.0
%if %{without bootstrap}
BuildRequires:	%{name}
%endif
Requires:	%{name}-libs = %{version}-%{release}
# ix86 cannot build this: linking the compiler against LLVM exhausts the 32-bit
# address space even with -Dstrip and -Doptimize=ReleaseSmall ("LLVM ERROR: out
# of memory"), and the cmake zig2.c bootstrap needs ~12 GB in a single cc1.
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zig is a general-purpose programming language and toolchain for
maintaining robust, optimal and reusable software. It has no hidden
control flow, no hidden memory allocations and no preprocessor or
macros. The toolchain doubles as a drop-in C and C++ cross-compiler.

%description -l pl.UTF-8
Zig to język programowania ogólnego przeznaczenia wraz z zestawem
narzędzi, służący do tworzenia niezawodnego, optymalnego
oprogramowania wielokrotnego użytku. Nie ma w nim ukrytego przepływu
sterowania, ukrytych alokacji pamięci ani preprocesora czy makr.
Zestaw narzędzi działa również jako kompilator skrośny języków C i
C++.

%package libs
Summary:	Zig standard library and bundled libc sources
Summary(pl.UTF-8):	Biblioteka standardowa Ziga oraz dołączone źródła bibliotek C
Group:		Development/Languages
BuildArch:	noarch

%description libs
Zig standard library together with the bundled libc headers and
sources (musl, glibc, mingw-w64, wasi-libc) and compiler-rt that the
compiler needs in order to build and cross-compile programs.

%description libs -l pl.UTF-8
Biblioteka standardowa Ziga wraz z dołączonymi nagłówkami i źródłami
bibliotek C (musl, glibc, mingw-w64, wasi-libc) oraz compiler-rt,
potrzebnymi kompilatorowi do budowania i kompilacji skrośnej
programów.

%prep
%setup -q -n %{name}-%{zigver}
%if %{with bootstrap}
tar xJf %{SOURCE1}
%endif

%build
install -d build
cd build
%cmake .. \
	-DZIG_PIE=ON \
	-DZIG_SHARED_LLVM=ON \
	-DZIG_TARGET_TRIPLE=native \
	-DZIG_VERSION=%{zigver}

# build.zig links zigcpp and reads config.h, both produced by the cmake run above
%{__make} zigcpp
cd ..

%if %{with bootstrap}
ZIG=$(pwd)/%{prebuilt_dir}/zig
%else
ZIG=%{_bindir}/zig
%endif
export ZIG_GLOBAL_CACHE_DIR=$(pwd)/build/zig-cache
export ZIG_LOCAL_CACHE_DIR=$(pwd)/build/zig-cache
$ZIG build \
	--zig-lib=$(pwd)/lib \
	--prefix $(pwd)/build/stage3 \
	--build-id=sha1 \
	-Dconfig_h=$(pwd)/build/config.h \
	-Dcpu=baseline \
	-Denable-llvm \
	-Dno-langref=true \
	-Doptimize=ReleaseFast \
	-Dpie \
	-Dtarget=native \
	-Dversion-string=%{zigver}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT%{_prefix}/lib

# The cmake install target runs zig with a hardcoded --prefix and ignores
# DESTDIR, so the stage3 tree is copied in by hand instead.
cp -p build/stage3/bin/zig $RPM_BUILD_ROOT%{_bindir}
cp -a build/stage3/lib/zig $RPM_BUILD_ROOT%{_prefix}/lib

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE README.md
%attr(755,root,root) %{_bindir}/zig

%files libs
%defattr(644,root,root,755)
%{_prefix}/lib/%{name}
