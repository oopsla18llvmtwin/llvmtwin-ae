// http://stackoverflow.com/questions/30195204/how-to-parse-llvm-ir-line-by-line
// http://llvm.org/docs/doxygen/html/InstCount_8cpp_source.html
#include <iostream>
#include <string>
#include <set>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/ErrorOr.h>
#include <llvm/Pass.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/InstVisitor.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/Operator.h>
#include <llvm/Bitcode/BitcodeReader.h>
#include <llvm/Support/raw_ostream.h>

using namespace llvm;

namespace{
class InstCountPass : public FunctionPass, public InstVisitor<InstCountPass> {
  friend class InstVisitor<InstCountPass>;

  void visitFunction(Function &F) { 
    ++TotalFuncs;
  }
  void visitBasicBlock(BasicBlock &BB) { 
    ++TotalBlocks; 
  }

#define HANDLE_INST(N, OPCODE, CLASS) \
  void visit##OPCODE(CLASS &I) { ++NumInst[""#OPCODE]; ++TotalInsts; countSpecialInsts(&I); visitOperands(&I); }
#include <llvm/IR/Instruction.def>
  
  void visitInstruction(Instruction &I) {
    errs() << "Instruction Count does not know about " << I;
    llvm_unreachable(nullptr);
  }
  void countSpecialInsts(Instruction *I) {
    if (IntrinsicInst *II = dyn_cast<IntrinsicInst>(I)) {
      if (II->getIntrinsicID() == Intrinsic::psub)
        PSubCount++;
    } else if (GetElementPtrInst *GEPI = dyn_cast<GetElementPtrInst>(I)) {
      if (GEPI->isInBounds())
        GEPInboundsCount++;
    }
  }
  void visitOperands(User *U) {
    if (isa<ConstantExpr>(U)) {
      ConstantExpr *CE = dyn_cast<ConstantExpr>(U);
      if (Visited.find(CE) != Visited.end()) return;
      Visited.insert(CE);
      switch (CE->getOpcode()) {
      case Instruction::IntToPtr:
        NumConstExpr["inttoptr"]++;
        break;
      case Instruction::PtrToInt:
        NumConstExpr["ptrtoint"]++;
        break;
      case Instruction::GetElementPtr:
        NumConstExpr["getelementptr"]++;
        if (dyn_cast<GEPOperator>(CE)->isInBounds())
          ConstExprGEPInboundsCount++;
        break;
      }
    }
    for (auto I = U->op_begin(); I != U->op_end(); ++I) {
      Value *V = *I;
      if (!isa<ConstantExpr>(V)) continue;
      visitOperands(dyn_cast<ConstantExpr>(V));
    }
  }
public:
  static char ID;
  InstCountPass():FunctionPass(ID) { }
  
  virtual bool runOnFunction(Function &F);
  void finalize();

  int TotalInsts = 0;
  int TotalFuncs = 0;
  int TotalBlocks = 0;

  std::set<ConstantExpr *> Visited;
  std::map<std::string, int> NumInst;
  std::map<std::string, int> NumConstExpr;
  int PSubCount = 0;
  int GEPInboundsCount = 0;
  int ConstExprGEPInboundsCount = 0;
};

bool InstCountPass::runOnFunction(Function &F) {
  visit(F);
  return false;
}
void InstCountPass::finalize() {
  // lower keys.
  std::map<std::string, int> NumInstLowered;
  for (auto itr = NumInst.begin(); itr != NumInst.end(); itr++) {
    std::string str = itr->first;
    std::string str2 = str;
    std::transform(str.begin(), str.end(), str2.begin(), ::tolower);
    int val = itr->second;
    NumInstLowered[str2] = val;
  }
  NumInst = NumInstLowered;
}
}

char InstCountPass::ID = 0;
static RegisterPass<InstCountPass> X("hello", "Hello World Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);

int main(int argc, char *argv[]){
  if (argc != 2 && argc != 3) {
    std::cerr << "Usage : " << argv[0] << " <.bc file>" << std::endl;
    std::cerr << "Usage : " << argv[0] << " <.bc file> <distinguish-const-and-inst(y/n)>" << std::endl;
    return 1;
  }

  StringRef filename = argv[1];
  LLVMContext context;

  ErrorOr<std::unique_ptr<MemoryBuffer>> fileOrErr = 
    MemoryBuffer::getFileOrSTDIN(filename);
  if (std::error_code ec = fileOrErr.getError()) {
    errs() << "Error opening input file: " << ec.message() << "\n";
    return 2;
  }
  ErrorOr<Expected<std::unique_ptr<llvm::Module>>> moduleOrErr = 
    parseBitcodeFile(fileOrErr.get()->getMemBufferRef(), context);
  if (std::error_code ec = moduleOrErr.getError()) {
    errs() << "Error reading module : " << ec.message() << "\n";
    return 3;
  }

  Expected<std::unique_ptr<llvm::Module>> moduleExpct = std::move(moduleOrErr.get());
  std::unique_ptr<Module> m;
  if (moduleExpct) {
    m = std::move(moduleExpct.get());
  } else {
    errs() << "Error reading module\n";
    return 3;
  }
  
  InstCountPass *ip = new InstCountPass();
  for (auto fitr = m->getFunctionList().begin(); 
      fitr != m->getFunctionList().end(); fitr++) {
    Function &f = *fitr;
    ip->runOnFunction(f);
  }
  ip->finalize();
  std::cout << "Total " << ip->TotalInsts << std::endl;
  if (argc == 3 && argv[2][0] == 'y') {
    // Distinguish constexpr and inst.
    std::cout << "inst inttoptr " << ip->NumInst["inttoptr"] << std::endl;
    std::cout << "inst ptrtoint " << ip->NumInst["ptrtoint"] << std::endl;
    std::cout << "inst getelementptr_all " << ip->NumInst["getelementptr"] << std::endl;
    std::cout << "inst getelementptr_inbounds " << ip->GEPInboundsCount << std::endl;
    std::cout << "inst psub " << ip->PSubCount << std::endl;
    std::cout << "constexpr inttoptr " << ip->NumConstExpr["inttoptr"] << std::endl;
    std::cout << "constexpr ptrtoint " << ip->NumConstExpr["ptrtoint"] << std::endl;
    std::cout << "constexpr getelementptr_all " << ip->NumConstExpr["getelementptr"] << std::endl;
    std::cout << "constexpr getelementptr_inbounds " << ip->ConstExprGEPInboundsCount << std::endl;
  } else {
    std::cout << "inttoptr " << ip->NumInst["inttoptr"] + ip->NumConstExpr["inttoptr"] << std::endl;
    std::cout << "ptrtoint " << ip->NumInst["ptrtoint"] + ip->NumConstExpr["ptrtoint"] << std::endl;
    std::cout << "getelementptr_all " << ip->NumInst["getelementptr"] + ip->NumConstExpr["getelementptr"] << std::endl;
    std::cout << "getelementptr_inbounds " << ip->GEPInboundsCount + ip->ConstExprGEPInboundsCount << std::endl;
    std::cout << "psub " << ip->PSubCount << std::endl;
  }
  return 0;
}
