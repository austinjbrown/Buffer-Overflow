pwd=$(pwd)
# adds the RISCV toolchain to your path so that you can run the executables
echo "export PATH=\${PATH}:${pwd}/riscv_toolchain/riscv/bin:${pwd}/sim/bin" >> ~/.bashrc
echo "!!!!!! IMPORTANT !!!!!!"
echo "You must use this netid to develop your exploit. This netid must be one of the netids of the people in your group. If you switch groups, you will need to run this script again."
echo "Enter your netid:"
read netid
echo "export NETID=${netid}" >> ~/.bashrc
