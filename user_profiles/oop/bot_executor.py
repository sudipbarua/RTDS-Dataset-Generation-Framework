from NormalBot import *

if __name__ == '__main__':
        # we create a local log folder (if does not exist) and save the log file with time stamp
        # This is created to be used globally by all the classes and funtions
        # save paths to config file
        log_folder = 'local_execution_logs'
        if not os.path.exists(log_folder):
                os.mkdir(log_folder)
        # get the present working directory
        pwd = os.getcwd()
        # get the time stamp
        timestamp = dt.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_file_path = os.path.join(pwd, log_folder, f'bot_exe_log_{timestamp}.csv')
        log_txt_file_path = os.path.join(pwd, log_folder, f'execution_log_{timestamp}.txt')
        # read config file
        with open('log_file_path.yml', 'r') as f:
                paths = yaml.safe_load(f)
        paths['log_paths']['log_file_path'] = log_file_path
        paths['log_paths']['log_txt_file_path'] = log_txt_file_path
        # overwrite file paths to config file
        with open('log_file_path.yml', 'w') as f:
                yaml.dump(paths, f, default_style='"')

        bot_master = BotGenerator(60, 1, 1, 5)
        bot_master.build_bots()
        bot_master.save_bots()
        bot_master.normalbotList[0].schedule_processes(warmup_period=3)
        # bot_master.cdBotList[0].schedule_processes(warmup_period=3)
        # with open('/home/sudip/rtds_project/user_profiles/oop/normal_bots/normal_bot_0.pickle', 'rb') as f:
        # with open('cd_bots/cd_bot_0.pickle', 'rb') as f:
        # with open('normal_bots/normal_bot_3.pickle', 'rb') as f:
          #      loaded_bot = pickle.load(f)
           #     loaded_bot.schedule_processes(warmup_period=3)
